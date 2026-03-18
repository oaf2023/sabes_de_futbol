"""
Script de verificación del login y los endpoints principales.
Ejecutar desde c:\\sabes_de_futbol\\backend:
    python test_login.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test():
    with app.test_client() as c:
        print("=== TEST LOGIN DNI: 16695057 ===")
        r = c.post('/api/login', json={'dni': '16695057', 'password': '123456'})
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.get_json()}")

        print("\n=== TEST LOGIN DNI: 12345678 ===")
        r2 = c.post('/api/login', json={'dni': '12345678', 'password': '123456'})
        print(f"  Status: {r2.status_code}")
        print(f"  Response: {r2.get_json()}")

        print("\n=== TEST PARTIDOS ===")
        r3 = c.get('/api/partidos')
        print(f"  Status: {r3.status_code}")
        d = r3.get_json()
        if d:
            print(f"  nro_fecha: {d.get('nro_fecha')}")
            print(f"  cantidad partidos: {len(d.get('partidos', []))}")
        else:
            print(f"  Response: {d}")

if __name__ == '__main__':
    test()
