"""
Nombre: app.py
Fecha: 2026-03-04
Versión: 2.0
Creador: OAF
Propósito: Aplicación principal Flask API para SABES DE FUTBOL (Versión Dinámica).
Funcionamiento: Gestiona el registro de usuarios, login, obtención de partidos dinámicos, 
               procesamiento de jugadas y sorteos. Integración lista para N8N.
Fuentes de datos: Base de datos SQLite (sabes_de_futbol.db).
Ejemplo de uso: Ejecutar con 'python app.py'. Acceder a http://localhost:5000.
"""

import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Usuario, Pais, FechaSorteo, Partido, JugadaUsuario, FechaActual
from game_logic import (
    codificar_jugada, decodificar_jugada, 
    generar_resultados_aleatorios_bin, calcular_aciertos_bin
)

# ---------------------------------------------------------------------------
# Crear y configurar la app
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'webp', 'pdf'}

def save_upload(file, subfolder, nombre_base):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(dest_dir, exist_ok=True)
        filename = f"{nombre_base}.{ext}"
        file.save(os.path.join(dest_dir, filename))
        return os.path.join('uploads', subfolder, filename)
    return None

# ---------------------------------------------------------------------------
# Rutas de la API
# ---------------------------------------------------------------------------

@app.route('/api/register', methods=['POST'])
def register():
    dni       = request.form.get('dni', '').strip()
    telefono  = request.form.get('telefono', '').strip()
    email     = request.form.get('email', '').strip()
    direccion = request.form.get('direccion', '').strip()
    nombre    = request.form.get('nombre', '').strip()
    fecha_nac = request.form.get('fecha_nac', '').strip()
    password  = request.form.get('password', '')

    if not all([dni, telefono, direccion, fecha_nac, password]):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    if Usuario.query.get(dni):
        return jsonify({'error': 'Ese DNI ya está registrado'}), 409

    foto_paths = {}
    for campo in ['foto_dni_frente', 'foto_dni_dorso', 'foto_selfie']:
        archivo = request.files.get(campo)
        ruta = save_upload(archivo, dni, campo)
        foto_paths[campo] = ruta

    usuario = Usuario(
        dni=dni, telefono=telefono, email=email or None,
        direccion=direccion, nombre=nombre, fecha_nac=fecha_nac,
        foto_dni_frente=foto_paths.get('foto_dni_frente'),
        foto_dni_dorso=foto_paths.get('foto_dni_dorso'),
        foto_selfie=foto_paths.get('foto_selfie'),
    )
    usuario.set_password(password)

    db.session.add(usuario)
    db.session.commit()
    return jsonify({'message': 'Registro exitoso', 'usuario': usuario.to_dict()}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    dni, password = data.get('dni', '').strip(), data.get('password', '')

    if not dni or not password:
        return jsonify({'error': 'DNI y contraseña son requeridos'}), 400

    usuario = Usuario.query.get(dni)
    if not usuario or not usuario.check_password(password):
        return jsonify({'error': 'DNI o contraseña incorrectos'}), 401

    return jsonify({'message': 'Login exitoso', 'usuario': usuario.to_dict()}), 200

@app.route('/api/partidos', methods=['GET'])
def get_partidos():
    """Retorna los partidos de la fecha marcada como activa en FechaActual."""
    control = FechaActual.query.filter_by(activo=True).first()
    if not control:
        return jsonify({'error': 'No hay una fecha marcada como activa'}), 404
    
    fecha_activa = FechaSorteo.query.filter_by(
        nro_fecha=control.nro_fecha, 
        pais_id=control.pais_id
    ).first()

    if not fecha_activa:
        return jsonify({'error': 'La fecha activa no existe en el fixture'}), 404

    # Ordenar partidos por el campo 'orden'
    partidos_lista = sorted(fecha_activa.partidos, key=lambda x: x.orden)

    return jsonify({
        'nro_fecha': f"{fecha_activa.nro_fecha:05d}",
        'partidos': [
            {'numero': i+1, 'nombre': p.to_dict()['nombre']} 
            for i, p in enumerate(partidos_lista)
        ],
        'sorteado': all(p.resultado_real is not None for p in fecha_activa.partidos),
        'fecha_id': fecha_activa.id
    }), 200

@app.route('/api/jugada', methods=['POST'])
def guardar_jugada():
    """Acepta JSON: { 'dni': '...', 'jugadas': [ ['L','E',...], [...] ] }"""
    data = request.get_json(silent=True) or {}
    dni = data.get('dni', '').strip()
    # Soportamos tanto 'selecciones' (retrocompatibilidad) como 'jugadas' (múltiples)
    jugadas_raw = data.get('jugadas', [])
    if not jugadas_raw and 'selecciones' in data:
        jugadas_raw = [data['selecciones']]

    if not jugadas_raw:
        return jsonify({'error': 'No hay jugadas para procesar'}), 400

    usuario = Usuario.query.get(dni)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Validar saldo de fichas (1 ficha por jugada)
    costo_total = len(jugadas_raw)
    if usuario.fichas < costo_total:
        return jsonify({
            'error': 'Fichas insuficientes',
            'necesarias': costo_total,
            'actuales': usuario.fichas
        }), 402

    control = FechaActual.query.filter_by(activo=True).first()
    fecha_activa = FechaSorteo.query.filter_by(nro_fecha=control.nro_fecha, pais_id=control.pais_id).first() if control else None
    
    if not fecha_activa:
        return jsonify({'error': 'No hay una fecha activa válida'}), 404

    ids_creados = []
    for selecciones in jugadas_raw:
        if len(selecciones) != len(fecha_activa.partidos):
             continue
        
        binario = codificar_jugada(selecciones)
        nueva = JugadaUsuario(
            usuario_dni=dni,
            fecha_sorteo_id=fecha_activa.id,
            jugada_binaria=binario,
            monto_apostado=1
        )
        db.session.add(nueva)
        db.session.flush()
        ids_creados.append(nueva.id)

    if not ids_creados:
        return jsonify({'error': 'Ninguna jugada fue válida (revise cantidad de partidos)'}), 400

    usuario.fichas -= len(ids_creados)
    db.session.commit()

    return jsonify({
        'mensaje': f'Se grabaron {len(ids_creados)} jugadas correctamente.',
        'fichas_restantes': usuario.fichas,
        'jugadas_ids': ids_creados
    }), 201

@app.route('/api/usuario/<dni>/fichas', methods=['GET'])
def obtener_fichas(dni):
    usuario = Usuario.query.get(dni)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'fichas': usuario.fichas}), 200

@app.route('/api/sortear', methods=['POST'])
def sortear():
    """Ejecuta el sorteo para la fecha activa y calcula aciertos."""
    data = request.get_json(silent=True) or {}
    jugada_id = data.get('jugada_id')
    
    if not jugada_id:
        return jsonify({'error': 'ID de jugada requerido'}), 400
        
    jugada = JugadaUsuario.query.get(jugada_id)
    if not jugada:
        return jsonify({'error': 'Jugada no encontrada'}), 404

    fecha = FechaSorteo.query.get(jugada.fecha_sorteo_id)
    
    # Simular sorteo si no hay resultados reales
    partidos = sorted(fecha.partidos, key=lambda x: x.orden)
    n = len(partidos)
    
    # Generar resultados aleatorios para cada partido si no los tiene
    for p in partidos:
        if not p.resultado_real:
            p.resultado_real = generar_resultados_aleatorios_bin(1) # Reusamos lógica para 1
            # El helper devuelve un bitstring de 3 chars, ej '100'. Lo convertimos a L/E/V
            res_list = decodificar_jugada(p.resultado_real)
            p.resultado_real = res_list[0] if res_list else 'L'

    db.session.commit()

    # Re-codificar resultado real completo para calcular aciertos
    resultados_lista = [p.resultado_real for p in partidos]
    resultado_bin = codificar_jugada(resultados_lista)
    
    aciertos = calcular_aciertos_bin(jugada.jugada_binaria, resultado_bin)
    jugada.aciertos = aciertos
    db.session.commit()

    # N8N READINESS: Notificar a webhook externo si está configurado
    webhook_url = os.getenv('N8N_WEBHOOK_URL')
    if webhook_url:
        try:
            requests.post(webhook_url, json={
                'event': 'sorteo_finalizado',
                'jugada_id': jugada.id,
                'dni': jugada.usuario_dni,
                'aciertos': aciertos,
                'fecha_id': jugada.fecha_sorteo_id
            }, timeout=2)
        except Exception as e:
            app.logger.warning(f"Error notificado a N8N: {e}")

    # Formatear respuesta con los nombres de los partidos
    partidos_res = []
    for i, p in enumerate(partidos):
        partidos_res.append({
            'nombre': f"{p.equipo_local} vs {p.equipo_visitante}",
            'seleccion': decodificar_jugada(jugada.jugada_binaria[i*3:i*3+3])[0],
            'resultado': p.resultado_real
        })

    return jsonify({
        'aciertos': aciertos,
        'partidos': partidos_res,
        'jugada_id': jugada.id
    }), 200

@app.route('/api/historial/<dni>', methods=['GET'])
def historial(dni):
    usuario = Usuario.query.get(dni)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
        
    # Devolver jugadas ordenadas por fecha descendente
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

# Placeholder para N8N y compra de fichas
@app.route('/api/comprar-fichas', methods=['POST'])
def comprar_fichas():
    """Simula una compra de fichas sumando una cantidad fija (ej. 10)."""
    data = request.get_json(silent=True) or {}
    dni = data.get('dni', '').strip()
    
    if not dni:
        return jsonify({'error': 'DNI requerido'}), 400
        
    usuario = Usuario.query.get(dni)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
        
    # Sumamos 10 fichas como simulación de compra exitosa
    cantidad = 10
    usuario.fichas += cantidad
    db.session.commit()
    
    return jsonify({
        'message': f'Compra exitosa. Se sumaron {cantidad} fichas.',
        'fichas_actuales': usuario.fichas
    }), 200


@app.route('/api/jugada/<int:jugada_id>', methods=['GET'])
def obtener_detalle_jugada(jugada_id):
    jugada = JugadaUsuario.query.get(jugada_id)
    if not jugada:
        return jsonify({'error': 'Jugada no encontrada'}), 404

    fecha = FechaSorteo.query.get(jugada.fecha_sorteo_id)
    if not fecha:
        return jsonify({'error': 'Fecha no encontrada'}), 404

    partidos = sorted(fecha.partidos, key=lambda x: x.orden)
    selecciones = decodificar_jugada(jugada.jugada_binaria)

    partidos_res = []
    for i, p in enumerate(partidos):
        partidos_res.append({
            'nombre': f"{p.equipo_local} vs {p.equipo_visitante}",
            'seleccion': selecciones[i] if i < len(selecciones) else None,
            'resultado': p.resultado_real
        })

    return jsonify({
        'id': jugada.id,
        'nro_fecha': f"{fecha.nro_fecha:05d}",
        'aciertos': jugada.aciertos,
        'fecha_hora': jugada.fecha_registro.strftime('%d/%m/%Y %H:%M'),
        'partidos': partidos_res
    }), 200

# STATIC_DIR: ruta absoluta a la raíz del proyecto (donde están index.html, style.css, etc.)
# Usa ruta absoluta para que funcione tanto en local como en PythonAnywhere
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Sirve el frontend estático desde la raíz del proyecto."""
    if path != "" and os.path.exists(os.path.join(STATIC_DIR, path)):
        return send_from_directory(STATIC_DIR, path)
    else:
        return send_from_directory(STATIC_DIR, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
