# Nombre: services.py
# Fecha: 2026-03-09
# Utilidad: Capa de Servicios (Business Logic) para SABES DE FUTBOL.
# Conectado a API: No (Es consumido por app.py)
# Descripción: Separa la lógica de negocio del controlador. Maneja usuarios, jugadas y sorteos con soporte de concurrencia para Python 3.13+.
# Ejemplo: GameService.procesar_sorteo(jugada_id) -> Ejecuta cálculos de aciertos y notificaciones.

import os
import sys
import threading
import json
import requests
import mercadopago
from datetime import datetime
from models import db, Usuario, FechaSorteo, Partido, JugadaUsuario, FechaActual, PagoFichas, PasarelaPago, ResultadoFecha
from game_logic import (
    codificar_jugada, decodificar_jugada, 
    generar_resultados_aleatorios_bin, calcular_aciertos_bin
)

def ejecutar_tarea_concurrente(app, func, *args):
    """
    Ejecuta una función en un hilo separado si la versión de Python es >= 3.13.
    Maneja el contexto de la aplicación para permitir acceso a la base de datos.
    """
    def wrapper():
        with app.app_context():
            try:
                func(*args)
            except Exception as e:
                print(f"Error en tarea concurrente: {e}")

    if sys.version_info >= (3, 13):
        t = threading.Thread(target=wrapper)
        t.start()
        return t
    else:
        # Ejecución normal para versiones inferiores
        with app.app_context():
            return func(*args)

class UserService:
    @staticmethod
    def registrar_usuario(datos, fotos):
        dni = datos.get('dni')
        if Usuario.query.get(dni):
            return None, "Ese DNI ya está registrado", 409

        # Determinar si el perfil está completo
        campos_completos = all([
            datos.get('dni'),
            datos.get('telefono'),
            datos.get('direccion'),
            datos.get('nombre'),
            datos.get('fecha_nac'),
            fotos.get('foto_dni_frente'),
            fotos.get('foto_dni_dorso'),
            fotos.get('foto_selfie')
        ])
        
        usuario = Usuario(
            dni=dni,
            telefono=datos.get('telefono'),
            email=datos.get('email') or None,
            direccion=datos.get('direccion'),
            nombre=datos.get('nombre'),
            fecha_nac=datos.get('fecha_nac'),
            foto_dni_frente=fotos.get('foto_dni_frente'),
            foto_dni_dorso=fotos.get('foto_dni_dorso'),
            foto_selfie=fotos.get('foto_selfie'),
            completado='SI' if campos_completos else 'NO'
        )
        usuario.set_password(datos.get('password'))
        db.session.add(usuario)
        db.session.commit()
        return usuario, None, 201

    @staticmethod
    def actualizar_usuario(dni, datos, fotos):
        usuario = Usuario.query.get(dni)
        if not usuario: return None, "Usuario no encontrado", 404
        
        # Actualizar campos básicos
        if 'telefono' in datos: usuario.telefono = datos.get('telefono')
        if 'direccion' in datos: usuario.direccion = datos.get('direccion')
        if 'nombre' in datos: usuario.nombre = datos.get('nombre')
        if 'fecha_nac' in datos: usuario.fecha_nac = datos.get('fecha_nac')
        if 'email' in datos: usuario.email = datos.get('email')
        
        # Actualizar fotos si se proveen
        if fotos.get('foto_dni_frente'): usuario.foto_dni_frente = fotos.get('foto_dni_frente')
        if fotos.get('foto_dni_dorso'): usuario.foto_dni_dorso = fotos.get('foto_dni_dorso')
        if fotos.get('foto_selfie'): usuario.foto_selfie = fotos.get('foto_selfie')
        
        # Recalcular estado completado
        campos_completos = all([
            usuario.dni,
            usuario.telefono,
            usuario.direccion,
            usuario.nombre,
            usuario.fecha_nac,
            usuario.foto_dni_frente,
            usuario.foto_dni_dorso,
            usuario.foto_selfie
        ])
        usuario.completado = 'SI' if campos_completos else 'NO'
        
        db.session.commit()
        return usuario, None, 200

    @staticmethod
    def login(dni, password):
        usuario = Usuario.query.get(dni)
        if not usuario or not usuario.check_password(password):
            return None, "DNI o contraseña incorrectos", 401
        return usuario, None, 200

class GameService:
    @staticmethod
    def obtener_partidos_activos():
        control = FechaActual.query.filter_by(activo=True).first()
        if not control:
            return None, "No hay una fecha marcada como activa", 404
        
        fecha_activa = FechaSorteo.query.filter_by(
            nro_fecha=control.nro_fecha, 
            pais_id=control.pais_id
        ).first()

        if not fecha_activa:
            return None, "La fecha activa no existe en el fixture", 404

        return fecha_activa, None, 200

    @staticmethod
    def guardar_jugadas(dni, jugadas_raw):
        usuario = Usuario.query.get(dni)
        if not usuario:
            return None, "Usuario no encontrado", 404

        costo_total = len(jugadas_raw)
        if usuario.fichas < costo_total:
            return None, f"Fichas insuficientes ({usuario.fichas}/{costo_total})", 402

        control = FechaActual.query.filter_by(activo=True).first()
        fecha_activa = FechaSorteo.query.filter_by(nro_fecha=control.nro_fecha, pais_id=control.pais_id).first() if control else None

        if not fecha_activa:
            return None, "No hay una fecha activa válida", 404

        # Regla 1: No se puede jugar si la fecha ya comenzó
        # El límite es hasta las 23:59 del día anterior al primer partido
        ahora = datetime.utcnow()
        partidos_ordenados = sorted(fecha_activa.partidos, key=lambda x: x.orden)
        primer_partido_hora = next(
            (p.fecha_hora for p in partidos_ordenados if getattr(p, 'fecha_hora', None)),
            None
        )
        if primer_partido_hora and ahora >= primer_partido_hora:
            return None, "La fecha ya comenzó. No se pueden registrar nuevas jugadas.", 403

        # Regla 3: No se puede jugar una fecha anterior a la activa
        # (el frontend sólo muestra la activa, pero validamos en backend igualmente)

        # Regla: El usuario no puede tener más de una jugada en la misma fecha
        ya_jugada = JugadaUsuario.query.filter_by(
            usuario_dni=dni,
            fecha_sorteo_id=fecha_activa.id
        ).first()
        if ya_jugada:
            return None, "Ya jugaste esta fecha. No podés modificar una jugada guardada.", 409

        ids_creados = []
        for selecciones in jugadas_raw:
            if len(selecciones) != len(fecha_activa.partidos):
                continue

            binario = codificar_jugada(selecciones)
            nueva = JugadaUsuario(
                usuario_dni=dni,
                nro_fecha=fecha_activa.nro_fecha,
                fecha_sorteo_id=fecha_activa.id,
                jugada_binaria=binario,
                monto_apostado=1
            )
            db.session.add(nueva)
            db.session.flush()
            ids_creados.append(nueva.id)

        if not ids_creados:
            return None, "Ninguna jugada fue válida (verificá que todos los partidos estén marcados)", 400

        usuario.fichas -= len(ids_creados)
        db.session.commit()
        return {"fichas_restantes": usuario.fichas, "ids": ids_creados}, None, 201

    @staticmethod
    def procesar_sorteo(jugada_id):
        """
        Calcula aciertos SOLO cuando todos los partidos de la fecha tienen resultado_real
        cargado por el administrador. No genera resultados aleatorios.
        """
        jugada = JugadaUsuario.query.get(jugada_id)
        if not jugada: return

        fecha = FechaSorteo.query.get(jugada.fecha_sorteo_id)
        partidos = sorted(fecha.partidos, key=lambda x: x.orden)

        # Solo procesar si TODOS los partidos tienen resultado oficial
        if not all(p.resultado_real for p in partidos):
            return  # La fecha aún no terminó, no calculamos nada

        # Calcular aciertos comparando selección del usuario con resultados reales
        resultados_lista = [p.resultado_real for p in partidos]
        resultado_bin = codificar_jugada(resultados_lista)
        aciertos = calcular_aciertos_bin(jugada.jugada_binaria, resultado_bin)
        jugada.aciertos = aciertos
        db.session.commit()

        # Notificar N8N
        webhook_url = os.getenv('N8N_WEBHOOK_URL')
        if webhook_url:
            try:
                requests.post(webhook_url, json={
                    'event': 'sorteo_finalizado',
                    'jugada_id': jugada.id,
                    'dni': jugada.usuario_dni,
                    'aciertos': aciertos,
                    'fecha_id': jugada.fecha_sorteo_id
                }, timeout=5)
            except: pass

class PaymentService:
    @staticmethod
    def registrar_intento_pago(dni, cantidad_fichas, p_monto, pasarela_nombre, external_id):
        pago = PagoFichas(
            usuario_dni=dni,
            pasarela=pasarela_nombre,
            external_id=external_id,
            paquete=f'libre_{cantidad_fichas}',
            fichas=cantidad_fichas,
            monto=p_monto,
            estado='pendiente'
        )
        db.session.add(pago)
        db.session.commit()
        return pago

    @staticmethod
    def crear_preferencia_mercadopago(dni, cantidad_fichas):
        usuario = Usuario.query.get(dni)
        if not usuario:
            return None, "Usuario no encontrado", 404

        if not isinstance(cantidad_fichas, int) or cantidad_fichas < 1:
            return None, "Cantidad inválida", 400

        monto = float(cantidad_fichas)  # 1 ficha = $1 ARS
        label = f'{cantidad_fichas} fichas'

        access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN') or os.environ.get('MP_ACCESS_TOKEN')
        if not access_token:
            # Fallback manual si no hay token
            static_url = "https://link.mercadopago.com.ar/sabesdefutbol"
            PaymentService.registrar_intento_pago(
                dni, cantidad_fichas, monto,
                'mercadopago_manual', f'manual_{int(datetime.utcnow().timestamp())}'
            )
            return {'checkout_url': static_url, 'modo': 'manual'}, None, 200

        try:
            sdk = mercadopago.SDK(access_token)
            app_url = os.environ.get('APP_URL', 'http://127.0.0.1:5000')

            preference_data = {
                'items': [{
                    'title': f'Sabes de Fútbol – {label}',
                    'quantity': 1,
                    'unit_price': monto,
                    'currency_id': 'ARS',
                }],
                'payer': {'email': usuario.email or f'{dni}@sabedefutbol.com'},
                'back_urls': {
                    'success': f'{app_url}/?pago=success&dni={dni}',
                    'failure': f'{app_url}/?pago=failure&dni={dni}',
                    'pending': f'{app_url}/?pago=pending&dni={dni}',
                },
                'auto_approve': False,
                'notification_url': f'{app_url}/api/webhook/mercadopago',
                'metadata': {'dni': dni, 'cantidad_fichas': cantidad_fichas},
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response['response']

            if 'id' in preference:
                PaymentService.registrar_intento_pago(
                    dni, cantidad_fichas, monto,
                    'mercadopago', preference['id']
                )
                checkout_url = preference.get('init_point') or preference.get('sandbox_init_point')
                return {'checkout_url': checkout_url, 'modo': 'automático'}, None, 200

            return None, "Error al crear preferencia", 500
        except Exception as e:
            print(f"Error MP API: {e}")
            return None, str(e), 500

    @staticmethod
    def procesar_webhook_mercadopago(mp_id, topic):
        if topic not in ('payment', 'merchant_order'):
            return {'status': 'ignored'}, None, 200

        access_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN') or os.environ.get('MP_ACCESS_TOKEN')
        if not access_token:
            return None, "Mercado Pago no configurado", 503

        try:
            sdk = mercadopago.SDK(access_token)
            payment_info = sdk.payment().get(mp_id)
            payment = payment_info.get('response', {})

            if payment.get('status') != 'approved':
                return {'status': 'not_approved'}, None, 200

            preference_id = payment.get('preference_id')
            if not preference_id:
                return {'status': 'no_preference'}, None, 200

            pago = PagoFichas.query.filter_by(external_id=preference_id, estado='pendiente').first()
            if not pago:
                return {'status': 'already_processed_or_not_found'}, None, 200

            usuario = Usuario.query.get(pago.usuario_dni)
            if usuario:
                usuario.fichas += pago.fichas
                pago.estado = 'aprobado'
                pago.fecha_resolucion = datetime.utcnow()
                db.session.commit()
                return {'status': 'ok', 'fichas_acreditadas': pago.fichas}, None, 200

            return None, "Usuario no encontrado para el pago", 404
        except Exception as e:
            print(f"Error Webhook: {e}")
            return None, str(e), 500
