# Nombre: app.py
# Fecha: 2026-03-11
# Utilidad: Controlador Principal (API Layer) para SABES DE FUTBOL.
# Conectado a API: Sí (Flask REST API)
# Descripción: Maneja las rutas HTTP y delega la lógica de negocio a services.py.

import os
import hmac
import hashlib
from datetime import datetime as _dt, timezone as _tz, timedelta as _td
from flask import Flask, request, jsonify, send_from_directory

# Argentina UTC-3 fijo
_AR_TZ = _tz(_td(hours=-3))
def ahora_ar():
    return _dt.now(_AR_TZ).replace(tzinfo=None)
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
from models import db, Usuario, PasarelaPago, JugadaUsuario, FechaSorteo, Partido, FechaActual, Pais, PagoFichas, ResultadoFecha
from services import UserService, GameService, PaymentService, ejecutar_tarea_concurrente
from game_logic import decodificar_jugada
from auth import create_jwt_token, require_auth

ADMIN_SECRET = os.getenv('ADMIN_SECRET', '')

def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        secret = request.headers.get('X-Admin-Secret', '')
        if not ADMIN_SECRET or not hmac.compare_digest(secret, ADMIN_SECRET):
            return jsonify({'error': 'No autorizado'}), 403
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__)

# ---------------------------------------------------------------------------
# CORS — Solo orígenes permitidos
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    'https://www.sabesdefutbol.com',
    'https://sabesdefutbol.com',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)

# ---------------------------------------------------------------------------
# Rate Limiting — Protección contra fuerza bruta
# ---------------------------------------------------------------------------
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sabes_de_futbol.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend', 'dist'))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB máximo por archivo

db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers de Archivos
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
# Firmas de bytes (magic bytes) para validar contenido real de imágenes
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpg',      # JPEG
    b'\x89PNG': 'png',           # PNG
    b'RIFF': 'webp',             # WebP (parcial)
    b'GIF8': 'gif',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_image(file_storage):
    """Verifica que el contenido del archivo sea realmente una imagen."""
    header = file_storage.read(12)
    file_storage.seek(0)  # Rebobinar para que Flask pueda guardarlo
    for magic, _ in MAGIC_BYTES.items():
        if header.startswith(magic):
            return True
    return False

def sanitize_identificador(ident):
    """Limpia el identificador de usuario (puede ser nro de socio o nombre)."""
    if not ident: return ""
    return str(ident).strip()

def save_upload(file, identificador, campo):
    if file and allowed_file(file.filename):
        if not is_valid_image(file):
            return None  # Rechaza archivos que no son imágenes reales
        ext = file.filename.rsplit('.', 1)[1].lower()
        # Usamos el identificador (nombre o nro de socio) para la carpeta
        safe_id = "".join(c for c in str(identificador) if c.isalnum())
        if not safe_id:
            return None
        dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], safe_id)
        os.makedirs(dest_dir, exist_ok=True)
        filename = f"{campo}.{ext}"
        path = os.path.join(dest_dir, filename)
        file.save(path)
        return f"uploads/{safe_id}/{filename}"
    return None

# ---------------------------------------------------------------------------
# Stats Públicas (Login)
# ---------------------------------------------------------------------------
@app.route('/api/stats-public', methods=['GET'])
def stats_publicas():
    total_socios = Usuario.query.count()
    ultimo_socio = db.session.query(db.func.max(Usuario.numero_de_socio)).scalar() or 0
    return jsonify({
        'total_socios': total_socios + 1000,
        'ultimo_socio': ultimo_socio if ultimo_socio > 0 else 1000
    }), 200

# ---------------------------------------------------------------------------
# Endpoints Auth
# ---------------------------------------------------------------------------
@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    # El registro ahora es "ligero" (nombre de usuario y password)
    nombre_usuario = request.form.get('nombre_de_usuario')
    if not nombre_usuario:
        return jsonify({'error': 'Nombre de usuario es obligatorio'}), 400

    dni = request.form.get('dni', '')
    
    fotos = {}
    # Solo procesamos fotos si se envían (ahora opcionales en registro inicial)
    for campo in ['foto_dni_frente', 'foto_dni_dorso', 'foto_selfie']:
        archivo = request.files.get(campo)
        if archivo:
            # Usamos el nombre de usuario para la carpeta de uploads inicial
            fotos[campo] = save_upload(archivo, nombre_usuario, campo)

    usuario, error, code = UserService.registrar_usuario(request.form, fotos)
    if error: return jsonify({'error': error}), code
    
    # Generamos token para loguear automáticamente tras registro
    token = create_jwt_token(usuario.numero_de_socio)
    return jsonify({
        'message': 'Registro exitoso', 
        'usuario': usuario.to_dict(),
        'token': token
    }), 201


@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    identificador = data.get('socio') or data.get('usuario') or data.get('dni')
    
    if not identificador:
        return jsonify({'error': 'Número de socio o usuario requerido'}), 400
        
    usuario, error, code = UserService.login(identificador, data.get('password', ''))
    if error: return jsonify({'error': error}), code
    
    # El token ahora se basa en el numero_de_socio
    token = create_jwt_token(usuario.numero_de_socio)
    return jsonify({
        'token': token,
        'usuario': usuario.to_dict()
    }), 200


@app.route('/api/usuario/verificar-password', methods=['POST'])
@require_auth
@limiter.limit("5 per minute")
def verificar_password():
    data = request.get_json(silent=True) or {}
    password = data.get('password')
    # El DNI viene del JWT, no del body — evita que un usuario verifique contraseña de otro
    usuario, error, code = UserService.login(request.current_user_dni, password)
    if error: return jsonify({'error': 'Contraseña incorrecta'}), 401
    return jsonify({'message': 'Verificación exitosa'}), 200


@app.route('/api/usuario/actualizar', methods=['POST'])
@require_auth
def actualizar_socio():
    # El identificador del JWT es el número de socio
    socio_nro = str(request.current_user_dni)

    fotos = {}
    for campo in ['foto_dni_frente', 'foto_dni_dorso', 'foto_selfie']:
        archivo = request.files.get(campo)
        if archivo:
            fotos[campo] = save_upload(archivo, socio_nro, campo)
        else:
            fotos[campo] = None

    usuario, error, code = UserService.actualizar_usuario(socio_nro, request.form, fotos)
    if error: return jsonify({'error': error}), code
    return jsonify({'message': 'Perfil actualizado', 'usuario': usuario.to_dict()}), 200

# ---------------------------------------------------------------------------
# Endpoints Juego
# ---------------------------------------------------------------------------
@app.route('/api/partidos', methods=['GET'])
def get_partidos():
    from datetime import datetime as dt
    fecha, error, code = GameService.obtener_partidos_activos()
    if error: return jsonify({'error': error}), code

    partidos_lista = sorted(fecha.partidos, key=lambda x: x.orden)

    # Determinar si la fecha ya comenzó: comparar la hora del primer partido con ahora (Argentina)
    ahora = ahora_ar()
    primer_partido_hora = None
    for p in partidos_lista:
        if getattr(p, 'fecha_hora', None):
            primer_partido_hora = p.fecha_hora
            break

    # La fecha "comenzó" si el primer partido tiene hora y ya pasó.
    # Si ningún partido tiene fecha_hora configurada, se asume que ya comenzó
    # (la fecha está activa y sin horario = se juega/jugó sin restricción horaria).
    if primer_partido_hora:
        fecha_comenzada = ahora >= primer_partido_hora
    else:
        fecha_comenzada = True

    return jsonify({
        'nro_fecha': f"{fecha.nro_fecha:05d}",
        'fecha_id': fecha.id,
        'fecha_comenzada': fecha_comenzada,
        'primer_partido_hora': primer_partido_hora.isoformat() if primer_partido_hora else None,
        'sorteado': all(p.resultado_real is not None for p in fecha.partidos),
        'partidos': [
            {
                'numero': i + 1,
                'nombre': p.to_dict()['nombre'],
                'local': p.equipo_local,
                'visitante': p.equipo_visitante,
                'resultado': p.resultado_real,
                'goles_local': p.goles_local,
                'goles_visitante': p.goles_visitante,
                'fecha_hora': p.fecha_hora.isoformat() if getattr(p, 'fecha_hora', None) else None,
            }
            for i, p in enumerate(partidos_lista)
        ],
    }), 200


@app.route('/api/proxima-fecha', methods=['GET'])
def get_proxima_fecha():
    """Devuelve los partidos de la próxima fecha (activa+1) si existe y aún no está activa."""
    control = FechaActual.query.filter_by(activo=True).first()
    if not control:
        return jsonify({'proxima': None}), 200

    nro_proxima = control.nro_fecha + 1
    fecha = FechaSorteo.query.filter_by(nro_fecha=nro_proxima, pais_id=control.pais_id).first()
    if not fecha:
        return jsonify({'proxima': None}), 200

    partidos_lista = sorted(fecha.partidos, key=lambda x: x.orden)
    return jsonify({
        'proxima': {
            'nro_fecha': f"{fecha.nro_fecha:05d}",
            'fecha_id': fecha.id,
            'partidos': [
                {
                    'numero': i + 1,
                    'nombre': p.to_dict()['nombre'],
                    'local': p.equipo_local,
                    'visitante': p.equipo_visitante,
                    'fecha_hora': p.fecha_hora.isoformat() if getattr(p, 'fecha_hora', None) else None,
                }
                for i, p in enumerate(partidos_lista)
            ],
        }
    }), 200


@app.route('/api/jugada', methods=['POST'])
@require_auth
def guardar_jugada():
    data = request.get_json(silent=True) or {}
    jugadas = data.get('jugadas', [])
    if not jugadas and 'selecciones' in data:
        jugadas = [data['selecciones']]
    fecha_sorteo_id = data.get('fecha_sorteo_id')  # opcional, para próxima fecha

    # El identificador del JWT es el número de socio
    socio_nro = request.current_user_dni
    res, error, code = GameService.guardar_jugadas(socio_nro, jugadas, fecha_sorteo_id)
    if error: return jsonify({'error': error}), code
    return jsonify(res), 201


@app.route('/api/sortear', methods=['POST'])
@require_auth
def sortear():
    data = request.get_json(silent=True) or {}
    jugada_id = data.get('jugada_id')
    if not jugada_id:
        return jsonify({'error': 'ID de jugada requerido'}), 400

    # Verificar que la jugada pertenece al usuario autenticado
    jugada = JugadaUsuario.query.get(jugada_id)
    if not jugada:
        return jsonify({'error': 'Jugada no encontrada o acceso denegado'}), 403
    usuario_auth = UserService.buscar_usuario(request.current_user_dni)
    if not usuario_auth or (jugada.usuario_id != usuario_auth.id and jugada.usuario_dni != usuario_auth.dni):
        return jsonify({'error': 'Jugada no encontrada o acceso denegado'}), 403

    from flask import current_app
    ejecutar_tarea_concurrente(current_app._get_current_object(), GameService.procesar_sorteo, jugada_id)
    return jsonify({'message': 'Sorteo iniciado'}), 202


@app.route('/api/jugada/<int:jugada_id>', methods=['GET'])
@require_auth
def obtener_detalle_jugada(jugada_id):
    jugada = JugadaUsuario.query.get(jugada_id)
    if not jugada:
        return jsonify({'error': 'Jugada no encontrada'}), 404

    # Solo el dueño puede ver su jugada (soporta token con nro_socio o DNI)
    usuario_auth = UserService.buscar_usuario(request.current_user_dni)
    if not usuario_auth:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    pertenece = (
        jugada.usuario_id == usuario_auth.id or
        jugada.usuario_dni == usuario_auth.dni
    )
    if not pertenece:
        return jsonify({'error': 'Acceso denegado'}), 403

    fecha = FechaSorteo.query.get(jugada.fecha_sorteo_id)
    partidos = sorted(fecha.partidos, key=lambda x: x.orden)
    selecciones = decodificar_jugada(jugada.jugada_binaria)

    partidos_res = []
    for i, p in enumerate(partidos):
        partidos_res.append({
            'nombre': p.to_dict()['nombre'],
            'seleccion': selecciones[i] if i < len(selecciones) else None,
            'resultado': p.resultado_real
        })

    return jsonify({
        'id': jugada.id,
        'nro_fecha': f"{fecha.nro_fecha:05d}",
        'aciertos': jugada.aciertos if jugada.aciertos is not None else "?",
        'fecha_hora': jugada.fecha_registro.strftime('%d/%m/%Y %H:%M'),
        'partidos': partidos_res,
        'status': 'completado' if jugada.aciertos is not None else 'procesando'
    }), 200


@app.route('/api/historial/<dni_or_socio>', methods=['GET'])
@require_auth
def historial(dni_or_socio):
    # El token ya garantiza la identidad — usar directamente el usuario autenticado
    usuario = UserService.buscar_usuario(request.current_user_dni)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Buscar jugadas por usuario_id (nuevo) O usuario_dni (registros legacy)
    jugadas = (JugadaUsuario.query
               .filter(
                   db.or_(
                       JugadaUsuario.usuario_id == usuario.id,
                       JugadaUsuario.usuario_dni == usuario.dni
                   )
               )
               .order_by(JugadaUsuario.fecha_registro.desc()).all())
    res = []
    for j in jugadas:
        f = FechaSorteo.query.get(j.fecha_sorteo_id)
        res.append({
            'id': j.id,
            'nro_fecha': f"{f.nro_fecha:05d}" if f else "00000",
            'aciertos': j.aciertos,
            'fecha': j.fecha_registro.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(res), 200

@app.route('/api/mi-jugada-activa', methods=['GET'])
@require_auth
def mi_jugada_activa():
    """
    Devuelve la jugada más reciente del usuario en la fecha activa.
    Incluye cada partido con la selección del usuario, el resultado real (si ya finalizó),
    y un flag 'acierto' (True/False/None) para renderizar el fibrón verde/naranja.
    También devuelve estadísticas parciales cuando la fecha está en curso.
    """
    socio_nro = request.current_user_dni
    usuario = UserService.buscar_usuario(socio_nro)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    control = FechaActual.query.filter_by(activo=True).first()
    if not control:
        return jsonify({'jugada': None, 'motivo': 'sin_fecha_activa'}), 200

    fecha = FechaSorteo.query.filter_by(
        nro_fecha=control.nro_fecha,
        pais_id=control.pais_id
    ).first()
    if not fecha:
        return jsonify({'jugada': None, 'motivo': 'sin_fixture'}), 200

    jugada = (JugadaUsuario.query
              .filter(
                  db.or_(
                      db.and_(JugadaUsuario.usuario_id == usuario.id, JugadaUsuario.fecha_sorteo_id == fecha.id),
                      db.and_(JugadaUsuario.usuario_dni == usuario.dni, JugadaUsuario.fecha_sorteo_id == fecha.id)
                  )
              )
              .order_by(JugadaUsuario.fecha_registro.desc())
              .first())
    if not jugada:
        return jsonify({'jugada': None, 'motivo': 'sin_jugada'}), 200

    partidos = sorted(fecha.partidos, key=lambda x: x.orden)
    selecciones = decodificar_jugada(jugada.jugada_binaria)

    partidos_res = []
    aciertos_parciales = 0
    errores_parciales = 0
    finalizados = 0

    for i, p in enumerate(partidos):
        sel = selecciones[i] if i < len(selecciones) else None
        res = p.resultado_real
        acierto = None
        if res is not None:
            finalizados += 1
            acierto = (sel == res)
            if acierto:
                aciertos_parciales += 1
            else:
                errores_parciales += 1

        partidos_res.append({
            'nombre': f"{p.equipo_local} vs {p.equipo_visitante}",
            'local': p.equipo_local,
            'visitante': p.equipo_visitante,
            'seleccion': sel,
            'resultado': res,
            'goles_local': p.goles_local,
            'goles_visitante': p.goles_visitante,
            'fecha_hora': p.fecha_hora.isoformat() if getattr(p, 'fecha_hora', None) else None,
            'acierto': acierto,   # True = verde, False = naranja, None = pendiente
        })

    total = len(partidos_res)
    pct_aciertos = round(aciertos_parciales / finalizados * 100) if finalizados > 0 else 0
    pct_errores  = round(errores_parciales  / finalizados * 100) if finalizados > 0 else 0

    return jsonify({
        'jugada': {
            'id': jugada.id,
            'nro_fecha': f"{fecha.nro_fecha:05d}",
            'fecha_registro': jugada.fecha_registro.isoformat() if jugada.fecha_registro else None,
            'aciertos_totales': jugada.aciertos,           # None hasta que cierre la fecha
            'partidos': partidos_res,
            'finalizados': finalizados,
            'total': total,
            'aciertos_parciales': aciertos_parciales,
            'errores_parciales': errores_parciales,
            'pct_aciertos': pct_aciertos,
            'pct_errores': pct_errores,
        }
    }), 200


# ---------------------------------------------------------------------------
# Pagos
# ---------------------------------------------------------------------------
@app.route('/api/usuario/<identificador>/fichas', methods=['GET'])
@require_auth
def gestionar_fichas(identificador):
    # Usar directamente el usuario autenticado por token
    u = UserService.buscar_usuario(request.current_user_dni)
    if not u: return jsonify({'error': 'No existe'}), 404
    return jsonify({'fichas': u.fichas}), 200


@app.route('/api/usuario/estado-ultimo-pago', methods=['GET'])
@require_auth
def estado_ultimo_pago():
    socio_nro = str(request.current_user_dni)
    pago = PagoFichas.query.filter_by(
        usuario_dni=socio_nro
    ).order_by(PagoFichas.fecha_creacion.desc()).first()
    if not pago:
        return jsonify({'estado': None}), 200
    return jsonify({
        'estado': pago.estado,
        'fichas': pago.fichas,
        'fecha': pago.fecha_creacion.isoformat() if pago.fecha_creacion else None
    }), 200


@app.route('/api/usuario/pago/<int:pago_id>', methods=['GET'])
@require_auth
def estado_pago_por_id(pago_id):
    pago = PagoFichas.query.get(pago_id)
    if not pago or pago.usuario_dni != request.current_user_dni:
        return jsonify({'estado': None}), 404
    return jsonify({
        'estado': pago.estado,
        'fichas': pago.fichas,
        'fecha': pago.fecha_creacion.isoformat() if pago.fecha_creacion else None
    }), 200


@app.route('/api/iniciar-pago', methods=['POST'])
@require_auth
def iniciar_pago():
    data = request.get_json(silent=True) or {}
    cantidad = data.get('cantidad')
    if not cantidad:
        return jsonify({'error': 'Faltan datos: cantidad requerida'}), 400
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        return jsonify({'error': 'cantidad debe ser un número entero'}), 400
    if cantidad < 1:
        return jsonify({'error': 'La cantidad mínima es 1 ficha'}), 400

    # Identificador viene del JWT (Socio)
    socio_nro = str(request.current_user_dni)
    res, error, code = PaymentService.crear_preferencia_mercadopago(socio_nro, cantidad)
    if error: return jsonify({'error': error}), code
    # Devolver también el id del registro de pago para que el frontend haga polling preciso
    pago = PagoFichas.query.filter_by(
        usuario_dni=socio_nro
    ).order_by(PagoFichas.fecha_creacion.desc()).first()
    if pago:
        res['pago_id'] = pago.id
    return jsonify(res), 200


@app.route('/api/webhook/mercadopago', methods=['POST'])
def webhook_mercadopago():
    # Verificar firma HMAC de MercadoPago (si hay secret configurado)
    mp_webhook_secret = os.getenv('MERCADOPAGO_WEBHOOK_SECRET', '')
    if mp_webhook_secret:
        x_signature = request.headers.get('x-signature', '')
        x_request_id = request.headers.get('x-request-id', '')
        data_id = request.args.get('data.id', '') or (request.get_json(silent=True) or {}).get('data', {}).get('id', '')

        manifest = f"id:{data_id};request-id:{x_request_id};"
        expected = hmac.new(
            mp_webhook_secret.encode('utf-8'),
            manifest.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Extraer ts y v1 del header x-signature
        sig_parts = dict(part.split('=', 1) for part in x_signature.split(',') if '=' in part)
        received = sig_parts.get('v1', '')

        if not hmac.compare_digest(expected, received):
            return jsonify({'error': 'Firma inválida'}), 400

    # Procesar el webhook
    topic = request.args.get('topic') or request.args.get('type')
    mp_id = request.args.get('id') or request.args.get('data.id')

    if not topic or not mp_id:
        data = request.get_json(silent=True) or {}
        topic = data.get('type', '')
        mp_id = str(data.get('data', {}).get('id', ''))

    res, error, code = PaymentService.procesar_webhook_mercadopago(mp_id, topic)
    if error: return jsonify({'error': error}), code
    return jsonify(res), 200

# ---------------------------------------------------------------------------
# Endpoints Admin
# ---------------------------------------------------------------------------

@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_stats():
    socios     = db.session.execute(db.text('SELECT COUNT(*) FROM usuarios')).scalar()
    completos  = db.session.execute(db.text("SELECT COUNT(*) FROM usuarios WHERE completado='SI'")).scalar()
    jugadas    = db.session.execute(db.text('SELECT COUNT(*) FROM jugadas_usuario')).scalar()
    fichas_tot = db.session.execute(db.text('SELECT COALESCE(SUM(fichas),0) FROM usuarios')).scalar()
    pagos_ok   = db.session.execute(db.text("SELECT COUNT(*) FROM pagos_fichas WHERE estado='aprobado'")).scalar()
    ultimos    = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(10).all()
    fechas_act = db.session.execute(db.text(
        'SELECT fa.nro_fecha, fa.pais_id, fa.activo, p.nombre as pais '
        'FROM fecha_actual fa LEFT JOIN paises p ON fa.pais_id = p.id'
    )).fetchall()
    return jsonify({
        'socios': socios, 'completos': completos, 'jugadas': jugadas,
        'fichas_total': fichas_tot, 'pagos_ok': pagos_ok,
        'ultimos_socios': [u.to_dict() for u in ultimos],
        'fechas_activas': [dict(r._mapping) for r in fechas_act]
    }), 200


@app.route('/api/admin/paises', methods=['GET'])
@require_admin
def admin_paises():
    paises = Pais.query.order_by(Pais.id).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in paises]), 200


@app.route('/api/admin/fechas', methods=['GET'])
@require_admin
def admin_fechas():
    pais_id = request.args.get('pais_id', type=int)
    q = FechaSorteo.query
    if pais_id:
        q = q.filter_by(pais_id=pais_id)
    fechas = q.order_by(FechaSorteo.nro_fecha).all()
    return jsonify([{'id': f.id, 'nro_fecha': f.nro_fecha, 'pais_id': f.pais_id} for f in fechas]), 200


@app.route('/api/admin/fecha-activa', methods=['GET'])
@require_admin
def admin_fecha_activa():
    pais_id = request.args.get('pais_id', type=int)
    q = FechaActual.query
    if pais_id:
        q = q.filter_by(pais_id=pais_id)
    rows = q.all()
    return jsonify([r.to_dict() for r in rows]), 200


@app.route('/api/admin/activar-fecha', methods=['POST'])
@require_admin
def admin_activar_fecha():
    data    = request.get_json(silent=True) or {}
    pais_id = data.get('pais_id')
    nro     = data.get('nro_fecha')
    if not pais_id or nro is None:
        return jsonify({'error': 'Faltan pais_id o nro_fecha'}), 400
    fa = FechaActual.query.filter_by(pais_id=pais_id).first()
    if fa:
        fa.nro_fecha = nro
        fa.activo    = True
    else:
        db.session.add(FechaActual(nro_fecha=nro, pais_id=pais_id, activo=True))
    db.session.commit()
    return jsonify({'ok': True, 'nro_fecha': nro}), 200


@app.route('/api/admin/partidos', methods=['GET'])
@require_admin
def admin_partidos():
    pais_id   = request.args.get('pais_id', type=int, default=1)
    nro_fecha = request.args.get('nro_fecha', type=int)
    fs = FechaSorteo.query.filter_by(pais_id=pais_id, nro_fecha=nro_fecha).first() if nro_fecha else None
    if not fs:
        return jsonify({'partidos': [], 'fs_id': None}), 200
    ps = sorted(fs.partidos, key=lambda p: p.orden)
    return jsonify({
        'fs_id': fs.id,
        'partidos': [{
            'id': p.id, 'orden': p.orden,
            'local': p.equipo_local, 'visitante': p.equipo_visitante,
            'goles_local': p.goles_local, 'goles_visitante': p.goles_visitante,
            'resultado': p.resultado_real,
            'fecha_hora': p.fecha_hora.isoformat() if p.fecha_hora else None,
        } for p in ps]
    }), 200


@app.route('/api/admin/resultado', methods=['POST'])
@require_admin
def admin_resultado():
    from datetime import datetime as dt
    from game_logic import codificar_jugada as _cod
    data = request.get_json(silent=True) or {}
    pid  = data.get('partido_id')
    gl   = data.get('goles_local')
    gv   = data.get('goles_visitante')
    res  = data.get('resultado')  # 'L', 'E', 'V' o None
    if pid is None:
        return jsonify({'error': 'partido_id requerido'}), 400
    p = Partido.query.get(pid)
    if not p:
        return jsonify({'error': 'Partido no encontrado'}), 404
    p.goles_local     = gl
    p.goles_visitante = gv
    p.resultado_real  = res if res in ('L', 'E', 'V') else None
    db.session.commit()

    # Si todos los partidos de la fecha finalizaron:
    fecha = FechaSorteo.query.get(p.fecha_sorteo_id)
    if fecha and all(pt.resultado_real is not None for pt in fecha.partidos):
        partidos_ord = sorted(fecha.partidos, key=lambda x: x.orden)
        resultados_lista = [pt.resultado_real for pt in partidos_ord]
        binario = _cod(resultados_lista)

        # 1. Registrar resultado oficial en tabla 'resultados' (una sola vez)
        existe = ResultadoFecha.query.filter_by(
            nro_fecha=fecha.nro_fecha,
            pais=fecha.pais_id
        ).first()
        if not existe:
            db.session.add(ResultadoFecha(
                nro_fecha=fecha.nro_fecha,
                jugada_binaria=binario,
                pais=fecha.pais_id,
                fecha_revision=ahora_ar()
            ))

        # 2. Recalcular aciertos para TODAS las jugadas de esta fecha
        from game_logic import calcular_aciertos_bin as _calc
        jugadas_fecha = JugadaUsuario.query.filter_by(fecha_sorteo_id=fecha.id).all()
        for jug in jugadas_fecha:
            aciertos = _calc(jug.jugada_binaria, binario)
            jug.aciertos = aciertos

        db.session.commit()

    return jsonify({'ok': True}), 200


@app.route('/api/admin/nueva-fecha', methods=['POST'])
@require_admin
def admin_nueva_fecha():
    data     = request.get_json(silent=True) or {}
    pais_id  = data.get('pais_id')
    nro      = data.get('nro_fecha')
    partidos = data.get('partidos', [])  # [{local, visitante, fecha_hora}, ...]
    if not pais_id or not nro:
        return jsonify({'error': 'Faltan pais_id o nro_fecha'}), 400
    if FechaSorteo.query.filter_by(pais_id=pais_id, nro_fecha=nro).first():
        return jsonify({'error': f'Ya existe la fecha #{nro} para este país'}), 409
    fs = FechaSorteo(nro_fecha=nro, pais_id=pais_id)
    db.session.add(fs)
    db.session.flush()
    from datetime import datetime as dt
    for idx, p in enumerate(partidos):
        fh = None
        if p.get('fecha_hora'):
            try:
                fh = dt.fromisoformat(p['fecha_hora'])
            except ValueError:
                pass
        db.session.add(Partido(
            fecha_sorteo_id=fs.id, orden=idx+1,
            equipo_local=p.get('local','').strip(),
            equipo_visitante=p.get('visitante','').strip(),
            fecha_hora=fh
        ))
    db.session.commit()
    return jsonify({'ok': True, 'fs_id': fs.id}), 201


@app.route('/api/admin/socios', methods=['GET'])
@require_admin
def admin_socios():
    filtro = request.args.get('q', '').strip()
    q = Usuario.query
    if filtro:
        filtro_like = f'%{filtro}%'
        q = q.filter(
            db.or_(
                Usuario.numero_de_socio.like(filtro_like),
                Usuario.nombre_de_usuario.like(filtro_like),
                Usuario.nombre.like(filtro_like),
                Usuario.dni.like(filtro_like)
            )
        )
    socios = q.order_by(Usuario.fecha_registro.desc()).limit(200).all()
    return jsonify([u.to_dict() for u in socios]), 200


@app.route('/api/admin/socio/<identificador>', methods=['GET'])
@require_admin
def admin_get_socio(identificador):
    u = UserService.buscar_usuario(identificador)
    if not u:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(u.to_dict()), 200


@app.route('/api/admin/socio/<identificador>', methods=['POST'])
@require_admin
def admin_update_socio(identificador):
    u = UserService.buscar_usuario(identificador)
    if not u:
        return jsonify({'error': 'No encontrado'}), 404
    data = request.get_json(silent=True) or {}
    if 'nombre'    in data: u.nombre    = data['nombre']
    if 'nombre_de_usuario' in data: u.nombre_de_usuario = data['nombre_de_usuario']
    if 'numero_de_socio' in data: u.numero_de_socio = data['numero_de_socio']
    if 'dni'       in data: u.dni       = data['dni']
    if 'email'     in data: u.email     = data['email']
    if 'telefono'  in data: u.telefono  = data['telefono']
    if 'fichas'    in data: u.fichas    = int(data['fichas'])
    if 'completado' in data: u.completado = data['completado']
    if data.get('nueva_password'):
        u.set_password(data['nueva_password'])
    db.session.commit()
    return jsonify({'ok': True}), 200


@app.route('/api/admin/migrar-pagos-fichas', methods=['POST'])
@require_admin
def admin_migrar_pagos_fichas():
    """Migración puntual: recrea tabla pagos_fichas con esquema correcto del ORM."""
    import sqlite3 as _sqlite3
    try:
        con = _sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("PRAGMA table_info(pagos_fichas)")
        cols = [r[1] for r in cur.fetchall()]

        if cols == ['id','usuario_dni','pasarela','external_id','paquete','fichas','monto','moneda','estado','fecha_creacion','fecha_resolucion']:
            con.close()
            return jsonify({'ok': True, 'msg': 'tabla ya tiene esquema correcto', 'columnas': cols}), 200

        cur.execute("SELECT COUNT(*) FROM pagos_fichas")
        total = cur.fetchone()[0]

        con.execute("PRAGMA foreign_keys = OFF")
        con.execute("DROP TABLE pagos_fichas")
        con.execute("""
            CREATE TABLE pagos_fichas (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                usuario_dni VARCHAR(20) NOT NULL,
                pasarela VARCHAR(50) NOT NULL,
                external_id VARCHAR(200),
                paquete VARCHAR(50) NOT NULL,
                fichas INTEGER NOT NULL,
                monto FLOAT NOT NULL,
                moneda VARCHAR(10) DEFAULT 'ARS',
                estado VARCHAR(20) DEFAULT 'pendiente',
                fecha_creacion DATETIME,
                fecha_resolucion DATETIME,
                FOREIGN KEY(usuario_dni) REFERENCES usuarios(dni)
            )
        """)
        con.commit()

        cur.execute("PRAGMA table_info(pagos_fichas)")
        cols_nuevas = [r[1] for r in cur.fetchall()]
        con.close()
        return jsonify({'ok': True, 'msg': f'tabla recreada (habia {total} registros)', 'columnas': cols_nuevas}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/admin/acreditar-fichas', methods=['POST'])
@require_admin
def admin_acreditar_fichas():
    data   = request.get_json(silent=True) or {}
    identificador = data.get('usuario_id') or data.get('dni')
    cant   = data.get('cantidad', 0)
    motivo = data.get('motivo', 'admin_manual')
    if not identificador or cant <= 0:
        return jsonify({'error': 'usuario_id/dni y cantidad requeridos'}), 400
    
    u = UserService.buscar_usuario(identificador)
    
    if not u:
        return jsonify({'error': 'Socio no encontrado'}), 404
    
    u.fichas += cant
    db.session.add(PagoFichas(
        usuario_dni=str(u.dni or u.numero_de_socio), pasarela='admin_manual',
        paquete=f'manual_{motivo}', fichas=cant, monto=0,
        estado='aprobado', fecha_resolucion=db.func.now()
    ))
    db.session.commit()
    return jsonify({'ok': True, 'fichas_nuevas': u.fichas}), 200


@app.route('/api/admin/pagos', methods=['GET'])
@require_admin
def admin_pagos():
    estado = request.args.get('estado', 'todos')
    q = PagoFichas.query
    if estado != 'todos':
        q = q.filter_by(estado=estado)
    pagos = q.order_by(PagoFichas.fecha_creacion.desc()).limit(100).all()
    result = []
    for p in pagos:
        d = p.to_dict()
        u = Usuario.query.get(p.usuario_dni)
        d['nombre'] = u.nombre if u else None
        result.append(d)
    return jsonify(result), 200


@app.route('/api/admin/pago/<int:pago_id>/aprobar', methods=['POST'])
@require_admin
def admin_aprobar_pago(pago_id):
    p = PagoFichas.query.get(pago_id)
    if not p:
        return jsonify({'error': 'No encontrado'}), 404
    p.estado = 'aprobado'
    p.fecha_resolucion = db.func.now()
    u = Usuario.query.get(p.usuario_dni)
    if u:
        u.fichas += p.fichas
    db.session.commit()
    return jsonify({'ok': True}), 200


@app.route('/api/admin/pago/<int:pago_id>/rechazar', methods=['POST'])
@require_admin
def admin_rechazar_pago(pago_id):
    p = PagoFichas.query.get(pago_id)
    if not p:
        return jsonify({'error': 'No encontrado'}), 404
    p.estado = 'rechazado'
    p.fecha_resolucion = db.func.now()
    db.session.commit()
    return jsonify({'ok': True}), 200


@app.route('/api/admin/jugadas', methods=['GET'])
@require_admin
def admin_jugadas():
    rows = db.session.execute(db.text(
        'SELECT ju.id, ju.usuario_dni, u.nombre, ju.nro_fecha, ju.aciertos, ju.fecha_registro '
        'FROM jugadas_usuario ju LEFT JOIN usuarios u ON ju.usuario_dni=u.dni '
        'ORDER BY ju.fecha_registro DESC LIMIT 50'
    )).fetchall()
    return jsonify([dict(r._mapping) for r in rows]), 200


@app.route('/api/admin/partido/<int:partido_id>', methods=['DELETE'])
@require_admin
def admin_delete_partido(partido_id):
    p = Partido.query.get(partido_id)
    if not p:
        return jsonify({'error': 'Partido no encontrado'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'ok': True}), 200

# ---------------------------------------------------------------------------
# Frontend Servido
# ---------------------------------------------------------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/') or path.startswith('uploads/'):
        return jsonify({'error': 'Not found'}), 404
    full_path = os.path.join(STATIC_DIR, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, 'index.html')


if __name__ == '__main__':
    app.run(debug=False, port=5000)
