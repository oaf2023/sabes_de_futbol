"""
Nombre: models.py
Fecha: 2026-03-04
Versión: 2.0
Creador: OAF
Propósito: Definición de base de datos con SQLite + SQLAlchemy (Refactorizado para escalabilidad).
Funcionamiento: Define tablas para Usuarios, Países, Fechas de Sorteo, Partidos y Jugadas. 
               Implementa una relación de uno a muchos para los partidos por fecha.
Fuentes de datos: Base de datos local SQLite (sabes_de_futbol.db).
Ejemplo de uso: 
    nueva_jugada = JugadaUsuario(usuario_dni='...', fecha_sorteo_id=...)
    db.session.add(nueva_jugada)
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    dni         = db.Column(db.String(20), primary_key=True)
    telefono    = db.Column(db.String(30), nullable=False)
    email       = db.Column(db.String(120), nullable=True)
    direccion   = db.Column(db.String(200), nullable=False)
    nombre      = db.Column(db.String(100), nullable=True)
    fecha_nac   = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    foto_dni_frente = db.Column(db.String(300), nullable=True)
    foto_dni_dorso  = db.Column(db.String(300), nullable=True)
    foto_selfie     = db.Column(db.String(300), nullable=True)
    fecha_registro  = db.Column(db.DateTime, default=datetime.utcnow)
    fichas          = db.Column(db.Integer, default=0) # Nuevo: Sistema de fichas
    pais_id         = db.Column(db.Integer, db.ForeignKey('paises.id'), default=1) # Nuevo: País del usuario (1=Arg)
    completado      = db.Column(db.String(2), default='NO') # Nuevo: 'SI' o 'NO'

    jugadas = db.relationship('JugadaUsuario', backref='usuario', lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            'dni': self.dni,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'nombre': self.nombre,
            'fecha_nac': self.fecha_nac,
            'foto_selfie': self.foto_selfie,
            'fichas': self.fichas,
            'completado': self.completado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Pais(db.Model):
    __tablename__ = 'paises'
    id      = db.Column(db.Integer, primary_key=True)
    nombre  = db.Column(db.String(50), nullable=False)
    codigo  = db.Column(db.String(10), nullable=True) # ej: AR, ES

class FechaSorteo(db.Model):
    __tablename__ = 'fechas_sorteo'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nro_fecha   = db.Column(db.Integer, nullable=False)
    pais_id     = db.Column(db.Integer, db.ForeignKey('paises.id'), nullable=False)
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con partidos dinámicos
    partidos = db.relationship('Partido', backref='fecha_sorteo', lazy=True, cascade="all, delete-orphan")
    # Historial de jugadas
    jugadas  = db.relationship('JugadaUsuario', backref='fecha_sorteo', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nro_fecha': f"{self.nro_fecha:05d}",
            'pais_id': self.pais_id,
            'partidos': [p.to_dict() for p in self.partidos],
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'sorteado': all(p.resultado_real is not None for p in self.partidos) if self.partidos else False
        }

class Partido(db.Model):
    __tablename__ = 'partidos'
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_sorteo_id = db.Column(db.Integer, db.ForeignKey('fechas_sorteo.id'), nullable=False)
    equipo_local    = db.Column(db.String(100), nullable=False)
    equipo_visitante = db.Column(db.String(100), nullable=False)
    resultado_real   = db.Column(db.String(1), nullable=True)   # 'L', 'E', 'V'
    orden            = db.Column(db.Integer, default=0)
    fecha_hora       = db.Column(db.DateTime, nullable=True)
    goles_local      = db.Column(db.Integer, nullable=True)
    goles_visitante  = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': f"{self.equipo_local} vs {self.equipo_visitante}",
            'local': self.equipo_local,
            'visitante': self.equipo_visitante,
            'resultado': self.resultado_real,
            'goles_local': self.goles_local,
            'goles_visitante': self.goles_visitante,
            'orden': self.orden
        }

class JugadaUsuario(db.Model):
    __tablename__ = 'jugadas_usuario'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_dni     = db.Column(db.String(20), db.ForeignKey('usuarios.dni'), nullable=False)
    nro_fecha       = db.Column(db.Integer, nullable=False)  # columna legacy NOT NULL en la DB
    fecha_sorteo_id = db.Column(db.Integer, db.ForeignKey('fechas_sorteo.id'), nullable=True)
    jugada_binaria  = db.Column(db.String(500), nullable=False) # Aumentado para más partidos
    aciertos        = db.Column(db.Integer, nullable=True)
    monto_apostado  = db.Column(db.Integer, default=1)
    fecha_registro  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_dni': self.usuario_dni,
            'fecha_sorteo_id': self.fecha_sorteo_id,
            'jugada': self.jugada_binaria,
            'aciertos': self.aciertos,
            'monto': self.monto_apostado,
            'fecha': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class FechaActual(db.Model):
    __tablename__ = 'fecha_actual'
    id          = db.Column(db.Integer, primary_key=True)
    nro_fecha   = db.Column(db.Integer, nullable=False)
    pais_id     = db.Column(db.Integer, db.ForeignKey('paises.id'), nullable=False)
    activo      = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'nro_fecha': self.nro_fecha,
            'pais_id': self.pais_id,
            'activo': self.activo
        }


class PasarelaPago(db.Model):
    """
    Configura qué pasarela de pago usará cada país.
    Una fila por combinación pais/pasarela. Solo una activa por país.
    """
    __tablename__ = 'pasarelas_pago'

    id          = db.Column(db.Integer, primary_key=True)
    pais_id     = db.Column(db.Integer, db.ForeignKey('paises.id'), nullable=False)
    nombre      = db.Column(db.String(50), nullable=False)  # mercadopago, stripe, paypal
    activo      = db.Column(db.Boolean, default=False)
    # JSON con las credenciales de la pasarela (access_token, public_key, etc.)
    # En producción estas claves deben venir de variables de entorno, NO de la DB
    config_json = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'pais_id': self.pais_id,
            'nombre': self.nombre,
            'activo': self.activo
        }


class PagoFichas(db.Model):
    """
    Registro de cada intento de compra de fichas.
    Ciclo de vida: pendiente → aprobado | rechazado | cancelado
    """
    __tablename__ = 'pagos_fichas'

    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_dni         = db.Column(db.String(20), db.ForeignKey('usuarios.dni'), nullable=False)
    pasarela            = db.Column(db.String(50), nullable=False)   # mercadopago, stripe, paypal
    external_id         = db.Column(db.String(200), nullable=True)   # ID en la pasarela (preference_id, payment_id)
    paquete             = db.Column(db.String(50), nullable=False)    # starter, normal, pro
    fichas              = db.Column(db.Integer, nullable=False)
    monto               = db.Column(db.Float, nullable=False)
    moneda              = db.Column(db.String(10), default='ARS')
    estado              = db.Column(db.String(20), default='pendiente')  # pendiente, aprobado, rechazado, cancelado
    fecha_creacion      = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_resolucion    = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_dni': self.usuario_dni,
            'pasarela': self.pasarela,
            'external_id': self.external_id,
            'paquete': self.paquete,
            'fichas': self.fichas,
            'monto': self.monto,
            'moneda': self.moneda,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
        }
