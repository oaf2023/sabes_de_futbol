# activar_fecha.py
# Uso: python activar_fecha.py --fec 10 --pais 1
# Activa la fecha indicada para el país indicado en la tabla fecha_actual.

import argparse
import os
import sys

# Asegurar que encuentra los módulos del backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import app
from models import db, FechaActual, FechaSorteo, Pais

def activar_fecha(nro_fecha: int, pais_id: int):
    with app.app_context():
        # Verificar que el país existe
        pais = Pais.query.get(pais_id)
        if not pais:
            print(f"ERROR: No existe un país con id={pais_id}")
            sys.exit(1)

        # Verificar que existe esa fecha para ese país
        fecha = FechaSorteo.query.filter_by(nro_fecha=nro_fecha, pais_id=pais_id).first()
        if not fecha:
            print(f"ADVERTENCIA: No se encontró FechaSorteo con nro_fecha={nro_fecha} y pais_id={pais_id}")
            print("Se actualizará fecha_actual de todas formas.")

        # Buscar registro existente para ese país
        registro = FechaActual.query.filter_by(pais_id=pais_id).first()

        if registro:
            anterior = registro.nro_fecha
            registro.nro_fecha = nro_fecha
            registro.activo = True
            print(f"Actualizado: pais={pais.nombre} ({pais_id}) | fecha {anterior} → {nro_fecha}")
        else:
            registro = FechaActual(nro_fecha=nro_fecha, pais_id=pais_id, activo=True)
            db.session.add(registro)
            print(f"Creado: pais={pais.nombre} ({pais_id}) | nro_fecha={nro_fecha}")

        db.session.commit()
        print("OK — fecha_actual actualizada correctamente.")

        # Mostrar estado actual de la tabla
        print("\n--- Estado actual de fecha_actual ---")
        todos = FechaActual.query.all()
        for r in todos:
            p = Pais.query.get(r.pais_id)
            nombre_pais = p.nombre if p else f"pais_id={r.pais_id}"
            print(f"  id={r.id} | {nombre_pais} | nro_fecha={r.nro_fecha:05d} | activo={r.activo}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Activar fecha de jugada para un país')
    parser.add_argument('--fec', type=int, required=True, help='Número de fecha a activar (ej: 10)')
    parser.add_argument('--pais', type=int, required=True, help='ID del país (ej: 1 = Argentina)')
    args = parser.parse_args()

    activar_fecha(args.fec, args.pais)
