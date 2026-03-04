"""
Nombre: reseed.py
Fecha: 2026-03-04
Versión: 1.0
Creador: OAF
Propósito: Reinicializar la base de datos y cargar datos iniciales de prueba (15 partidos).
Funcionamiento: Borra la base de datos existente, crea las tablas y carga un fixture de 15 partidos para Argentina.
Fuentes de datos: Definiciones internas en el script.
Ejemplo de uso: python backend/reseed.py
"""

import os
import sys

# Añadir el directorio actual al path para importar modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Pais, FechaSorteo, Partido, FechaActual, Usuario

def reseed():
    with app.app_context():
        # Borrar y recrear todo
        db.drop_all()
        db.create_all()
        
        # 0. Crear Usuario de prueba
        user = Usuario(
            dni='12345678',
            telefono='123456789',
            direccion='Calle Falsa 123',
            fecha_nac='1990-01-01',
            fichas=100
        )
        user.set_password('1234')
        db.session.add(user)
        
        # 1. Crear País
        ar = Pais(nombre='Argentina', codigo='AR')
        db.session.add(ar)
        db.session.commit()
        
        # 2. Crear Fecha de Sorteo
        fs = FechaSorteo(nro_fecha=9, pais_id=ar.id)
        db.session.add(fs)
        db.session.commit()
        
        # 3. Cargar Partidos desde fixtures.json (Dinamismo REAL)
        import json
        fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures.json')
        with open(fixtures_path, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
            # Buscar la fecha 9
            fecha_data = next((item for item in data_json if item['nro_fecha'] == 9), None)
            partidos_nombres = fecha_data['partidos'] if fecha_data else []
        
        if not partidos_nombres:
            print("⚠️ No se encontraron partidos en fixtures.json para la fecha 9.")
            # Fallback a lista genérica si no hay archivo
            partidos_nombres = ['River vs Boca', 'Racing vs Huracán']

        for i, nombre in enumerate(partidos_nombres):
            teams = nombre.split(' vs ')
            partido = Partido(
                fecha_sorteo_id=fs.id,
                equipo_local=teams[0],
                equipo_visitante=teams[1],
                orden=i
            )
            db.session.add(partido)
            
        # 4. Establecer Fecha Actual
        fa = FechaActual(nro_fecha=9, pais_id=ar.id, activo=True)
        db.session.add(fa)
        
        db.session.commit()
        print(f"Base de datos reiniciada y cargada con {len(partidos_nombres)} partidos para la Fecha 9.")

if __name__ == '__main__':
    reseed()
