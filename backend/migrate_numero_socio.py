
import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Usuario, JugadaUsuario

def migrar_usuarios():
    with app.app_context():
        print("Iniciando migración de usuarios...")
        
        # 1. Obtener todos los usuarios que no tienen número de socio
        usuarios = Usuario.query.filter(Usuario.numero_de_socio == None).order_by(Usuario.fecha_registro).all()
        
        if not usuarios:
            print("No hay usuarios pendientes de migrar.")
            return

        # 2. Determinar el punto de inicio para el número de socio
        ultimo = Usuario.query.filter(Usuario.numero_de_socio != None).order_by(Usuario.numero_de_socio.desc()).first()
        proximo_nro = (ultimo.numero_de_socio + 1) if ultimo and ultimo.numero_de_socio else 1000

        print(f"Migrando {len(usuarios)} usuarios. Empezando desde el nro socio: {proximo_nro}")

        for u in usuarios:
            u.numero_de_socio = proximo_nro
            # Si no tiene nombre de usuario, usamos el DNI como nombre temporal
            if not u.nombre_de_usuario:
                u.nombre_de_usuario = f"user_{u.dni}"
            
            # Asociar jugadas existentes (usuario_dni -> usuario_id)
            # Buscamos jugadas que tengan usuario_dni pero no usuario_id
            jugadas_pendientes = JugadaUsuario.query.filter_by(usuario_dni=u.dni, usuario_id=None).all()
            for j in jugadas_pendientes:
                j.usuario_id = u.id
            
            proximo_nro += 1
            print(f"Usuario DNI {u.dni} -> Socio {u.numero_de_socio}")

        try:
            db.session.commit()
            print("Migración completada con éxito.")
        except Exception as e:
            db.session.rollback()
            print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrar_usuarios()
