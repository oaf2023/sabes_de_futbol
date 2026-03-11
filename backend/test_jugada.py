"""
Test completo del flujo: login → guardar jugada → sortear
Ejecutar desde: c:\\sabes_de_futbol\\backend
    python test_jugada.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

DNI = '16695057'
PASSWORD = 'oscar1234'

def test():
    with app.test_client() as c:
        # 1. Login
        print("=== 1. LOGIN ===")
        r = c.post('/api/login', json={'dni': DNI, 'password': PASSWORD})
        print(f"  Status: {r.status_code} | {r.get_json()}")
        if r.status_code != 200:
            print("  ❌ Login fallido, abortando.")
            return

        # 2. Partidos
        print("\n=== 2. PARTIDOS ===")
        r2 = c.get('/api/partidos')
        data_partidos = r2.get_json()
        print(f"  Status: {r2.status_code}")
        print(f"  nro_fecha: {data_partidos.get('nro_fecha')}, cantidad: {len(data_partidos.get('partidos', []))}")

        n_partidos = len(data_partidos.get('partidos', []))

        # 3. Guardar jugada
        print("\n=== 3. GUARDAR JUGADA ===")
        selecciones = ['L', 'E', 'V'] * (n_partidos // 3) + ['L'] * (n_partidos % 3)
        selecciones = selecciones[:n_partidos]
        print(f"  Selecciones ({len(selecciones)}): {selecciones}")
        r3 = c.post('/api/jugada', json={'dni': DNI, 'jugadas': [selecciones]})
        print(f"  Status: {r3.status_code} | {r3.get_json()}")

if __name__ == '__main__':
    test()
