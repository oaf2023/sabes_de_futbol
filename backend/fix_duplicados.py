"""
fix_duplicados.py
Elimina partidos duplicados en la fecha activa recargándola limpia desde fixtures.json.
Ejecutar UNA VEZ en PythonAnywhere: python fix_duplicados.py
"""
import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sabes_de_futbol.db')
FIXTURES_PATH = os.path.join(BASE_DIR, 'fixtures.json')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Ver partidos actuales de fecha 10
c.execute("""
    SELECT p.id, p.equipo_local, p.equipo_visitante, p.resultado_real, p.goles_local, p.goles_visitante
    FROM partidos p
    JOIN fechas_sorteo fs ON p.fecha_sorteo_id = fs.id
    JOIN paises pa ON fs.pais_id = pa.id
    WHERE fs.nro_fecha = 10 AND pa.nombre = 'Argentina'
    ORDER BY p.orden, p.id
""")
rows = c.fetchall()
print(f"Partidos en fecha 10 antes de fix: {len(rows)}")
for r in rows:
    print(f"  id={r['id']} | {r['equipo_local']} vs {r['equipo_visitante']} | {r['goles_local']}-{r['goles_visitante']} {r['resultado_real']}")

# Obtener fs_id
c.execute("""
    SELECT fs.id FROM fechas_sorteo fs
    JOIN paises pa ON fs.pais_id = pa.id
    WHERE fs.nro_fecha = 10 AND pa.nombre = 'Argentina'
""")
fs_row = c.fetchone()
if not fs_row:
    print("ERROR: No se encontró fecha 10 para Argentina")
    conn.close()
    exit(1)

fs_id = fs_row['id']
print(f"\nfs_id de fecha 10 = {fs_id}")

# Borrar TODOS los partidos de esta fecha
c.execute("DELETE FROM partidos WHERE fecha_sorteo_id = ?", (fs_id,))
print(f"Borrados {c.rowcount} partidos.")

# Recargar desde fixtures.json
with open(FIXTURES_PATH, 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

fecha10 = next((x for x in fixtures if x['nro_fecha'] == 10 and x.get('pais') == 'Argentina'), None)
if not fecha10:
    print("ERROR: fecha 10 no encontrada en fixtures.json")
    conn.close()
    exit(1)

insertados = 0
for idx, p in enumerate(fecha10['partidos']):
    if not isinstance(p, dict):
        continue
    fh = None
    if p.get('fecha_hora'):
        try:
            fh = datetime.fromisoformat(p['fecha_hora']).isoformat()
        except:
            pass
    c.execute("""
        INSERT INTO partidos (fecha_sorteo_id, equipo_local, equipo_visitante, resultado_real,
                              goles_local, goles_visitante, orden, fecha_hora)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (fs_id, p['local'], p['visitante'], p.get('resultado'),
          p.get('goles_local'), p.get('goles_visitante'), idx + 1, fh))
    insertados += 1

conn.commit()
print(f"Insertados {insertados} partidos limpios.")

# Verificar resultado final
c.execute("""
    SELECT id, equipo_local, equipo_visitante, goles_local, goles_visitante, resultado_real
    FROM partidos WHERE fecha_sorteo_id = ? ORDER BY orden
""", (fs_id,))
rows = c.fetchall()
print(f"\nPartidos en fecha 10 después de fix: {len(rows)}")
for r in rows:
    print(f"  id={r['id']} | {r['equipo_local']} vs {r['equipo_visitante']} | {r['goles_local']}-{r['goles_visitante']} {r['resultado_real']}")

conn.close()
print("\nFix completado. Hacer Reload en el panel Web.")
