# Nombre: app.py
# Fecha: 2026-03-11
# Utilidad: Controlador Principal (API Layer) para SABES DE FUTBOL.
# Conectado a API: Sí (Flask REST API)
# Descripción: Maneja las rutas HTTP y delega la lógica de negocio a services.py.

import os
import hmac
import hashlib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
from models import db, Usuario, PasarelaPago, JugadaUsuario, FechaSorteo
from services import UserService, GameService, PaymentService, ejecutar_tarea_concurrente
from game_logic import decodificar_jugada
from auth import create_jwt_token, require_auth

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

def sanitize_dni(dni):
    """Acepta solo dígitos en el DNI."""
    return ''.join(c for c in (dni or '') if c.isdigit())

def save_upload(file, dni, campo):
    if file and allowed_file(file.filename):
        if not is_valid_image(file):
            return None  # Rechaza archivos que no son imágenes reales
        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_dni = sanitize_dni(dni)
        if not safe_dni:
            return None
        dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], safe_dni)
        os.makedirs(dest_dir, exist_ok=True)
        filename = f"{campo}.{ext}"
        path = os.path.join(dest_dir, filename)
        file.save(path)
        return f"uploads/{safe_dni}/{filename}"
    return None

# ---------------------------------------------------------------------------
# Endpoints Auth
# ---------------------------------------------------------------------------
@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    dni = sanitize_dni(request.form.get('dni', ''))
    if not dni:
        return jsonify({'error': 'DNI es obligatorio y debe contener solo números'}), 400

    fotos = {}
    for campo in ['foto_dni_frente', 'foto_dni_dorso', 'foto_selfie']:
        archivo = request.files.get(campo)
        fotos[campo] = save_upload(archivo, dni, campo)

    usuario, error, code = UserService.registrar_usuario(request.form, fotos)
    if error: return jsonify({'error': error}), code
    return jsonify({'message': 'Registro exitoso', 'usuario': usuario.to_dict()}), 201


@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    usuario, error, code = UserService.login(data.get('dni', ''), data.get('password', ''))
    if error: return jsonify({'error': error}), code
    token = create_jwt_token(usuario.dni)
    return jsonify({'message': 'Login exitoso', 'usuario': usuario.to_dict(), 'token': token}), 200


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
    # DNI viene del JWT — ignora cualquier DNI en el body
    dni = request.current_user_dni

    fotos = {}
    for campo in ['foto_dni_frente', 'foto_dni_dorso', 'foto_selfie']:
        archivo = request.files.get(campo)
        if archivo:
            fotos[campo] = save_upload(archivo, dni, campo)
        else:
            fotos[campo] = None

    usuario, error, code = UserService.actualizar_usuario(dni, request.form, fotos)
    if error: return jsonify({'error': error}), code
    return jsonify({'message': 'Perfil actualizado', 'usuario': usuario.to_dict()}), 200

# ---------------------------------------------------------------------------
# Endpoints Juego
# ---------------------------------------------------------------------------
@app.route('/api/partidos', methods=['GET'])
def get_partidos():
    fecha, error, code = GameService.obtener_partidos_activos()
    if error: return jsonify({'error': error}), code

    partidos_lista = sorted(fecha.partidos, key=lambda x: x.orden)
    return jsonify({
        'nro_fecha': f"{fecha.nro_fecha:05d}",
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
        'sorteado': all(p.resultado_real is not None for p in fecha.partidos),
        'fecha_id': fecha.id
    }), 200


@app.route('/api/jugada', methods=['POST'])
@require_auth
def guardar_jugada():
    data = request.get_json(silent=True) or {}
    jugadas = data.get('jugadas', [])
    if not jugadas and 'selecciones' in data:
        jugadas = [data['selecciones']]

    # DNI viene del JWT
    res, error, code = GameService.guardar_jugadas(request.current_user_dni, jugadas)
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
    if not jugada or jugada.usuario_dni != request.current_user_dni:
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

    # Solo el dueño puede ver su jugada
    if jugada.usuario_dni != request.current_user_dni:
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


@app.route('/api/historial/<dni>', methods=['GET'])
@require_auth
def historial(dni):
    # Solo el propio usuario puede ver su historial
    if request.current_user_dni != dni:
        return jsonify({'error': 'Acceso denegado'}), 403

    jugadas = JugadaUsuario.query.filter_by(usuario_dni=dni).order_by(JugadaUsuario.fecha_registro.desc()).all()
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

# ---------------------------------------------------------------------------
# Pagos
# ---------------------------------------------------------------------------
@app.route('/api/usuario/<dni>/fichas', methods=['GET'])
@require_auth
def gestionar_fichas(dni):
    # Solo el propio usuario puede ver sus fichas
    if request.current_user_dni != dni:
        return jsonify({'error': 'Acceso denegado'}), 403

    u = Usuario.query.get(dni)
    if not u: return jsonify({'error': 'No existe'}), 404
    return jsonify({'fichas': u.fichas}), 200


@app.route('/api/iniciar-pago', methods=['POST'])
@require_auth
def iniciar_pago():
    data = request.get_json(silent=True) or {}
    paquete = data.get('paquete')
    if not paquete:
        return jsonify({'error': 'Faltan datos'}), 400

    # DNI viene del JWT
    res, error, code = PaymentService.crear_preferencia_mercadopago(request.current_user_dni, paquete)
    if error: return jsonify({'error': error}), code
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
