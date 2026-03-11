# migrate_fecha_hora.py
# Agrega columna fecha_hora a la tabla partidos si no existe.
# Ejecutar: python migrate_fecha_hora.py

import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sabes_de_futbol.db')
conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("PRAGMA table_info(partidos)")
cols = [row[1] for row in c.fetchall()]
print("Columnas actuales en partidos:", cols)

if 'fecha_hora' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN fecha_hora DATETIME")
    print("OK — columna fecha_hora agregada.")
else:
    print("OK — fecha_hora ya existe.")

if 'goles_local' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN goles_local INTEGER")
    print("OK — columna goles_local agregada.")
else:
    print("OK — goles_local ya existe.")

if 'goles_visitante' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN goles_visitante INTEGER")
    print("OK — columna goles_visitante agregada.")
else:
    print("OK — goles_visitante ya existe.")

conn.commit()
conn.close()
