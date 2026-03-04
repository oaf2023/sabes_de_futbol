import json
import os
from app import app
from models import db, Pais, FechaSorteo, FechaActual

def seed():
    with app.app_context():
        # 0. Asegurar tablas
        db.create_all() 

        # Cargar JSON
        json_path = os.path.join(os.path.dirname(__file__), 'fixtures.json')
        if not os.path.exists(json_path):
            print(f"Error: No se encontró {json_path}")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for i, item in enumerate(data):
            # 1. Pais
            nombre_pais = item.get('pais', 'Argentina')
            pais = Pais.query.filter_by(nombre=nombre_pais).first()
            if not pais:
                pais = Pais(nombre=nombre_pais, codigo=nombre_pais[:2].upper())
                db.session.add(pais)
                db.session.commit()
                print(f"País '{nombre_pais}' creado.")

            # 2. Fecha
            nro = item.get('nro_fecha')
            partidos = item.get('partidos', [])
            if len(partidos) != 13:
                print(f"Advertencia: La fecha {nro} no tiene 13 partidos.")
                continue

            fecha_db = FechaSorteo.query.filter_by(nro_fecha=nro, pais_id=pais.id).first()
            if not fecha_db:
                fecha_db = FechaSorteo(
                    nro_fecha=nro,
                    pais_id=pais.id,
                    **{f"partido_{i+1}": p for i, p in enumerate(partidos)}
                )
                db.session.add(fecha_db)
                db.session.commit()
                print(f"Fecha {nro:05d} ({nombre_pais}) creada.")
            
            # 3. Marcar la PRIMERA fecha del archivo como activa
            if i == 0:
                control = FechaActual.query.filter_by(activo=True).first()
                if not control:
                    control = FechaActual(nro_fecha=nro, pais_id=pais.id, activo=True)
                    db.session.add(control)
                else:
                    control.nro_fecha = nro
                    control.pais_id = pais.id
                db.session.commit()
                print(f"Fecha {nro} marcada como ACTIVA en la tabla de control.")

if __name__ == "__main__":
    seed()
