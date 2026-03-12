"""
Script de migración puntual: renombrar columna cantidad_fichas → fichas
en la tabla pagos_fichas de SQLite.

Uso: python backend/fix_columna_fichas.py
"""
import sqlite3
import os
import sys

# Buscar la BD en rutas habituales
BD_PATHS = [
    os.path.join(os.path.dirname(__file__), 'sabes_de_futbol.db'),
    os.path.join(os.path.dirname(__file__), '..', 'sabes_de_futbol.db'),
]

db_path = None
for p in BD_PATHS:
    if os.path.exists(p):
        db_path = os.path.abspath(p)
        break

if not db_path:
    print("ERROR: No se encontró sabes_de_futbol.db. Rutas buscadas:")
    for p in BD_PATHS:
        print(f"  {os.path.abspath(p)}")
    sys.exit(1)

print(f"BD encontrada: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verificar columnas actuales
cur.execute("PRAGMA table_info(pagos_fichas)")
cols = {row[1]: row for row in cur.fetchall()}
print(f"Columnas actuales en pagos_fichas: {list(cols.keys())}")

if 'fichas' in cols:
    print("✓ La columna ya se llama 'fichas'. No se requiere migración.")
    conn.close()
    sys.exit(0)

if 'cantidad_fichas' not in cols:
    print("ERROR: No existe 'cantidad_fichas' ni 'fichas'. Revisar la tabla manualmente.")
    conn.close()
    sys.exit(1)

print("Migrando: cantidad_fichas → fichas ...")

# SQLite < 3.25 no soporta RENAME COLUMN, usamos recreación de tabla
# Obtener definición completa
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='pagos_fichas'")
create_sql = cur.fetchone()[0]
print(f"SQL original: {create_sql}")

# Reemplazar nombre de columna en la definición
new_create_sql = create_sql.replace('cantidad_fichas', 'fichas')

# Listar columnas para el SELECT
col_names_old = [row[1] for row in cols.values()]
col_names_new = ['fichas' if c == 'cantidad_fichas' else c for c in col_names_old]

old_cols_str = ', '.join(col_names_old)
new_cols_str = ', '.join(col_names_new)

conn.execute("BEGIN")
try:
    conn.execute("ALTER TABLE pagos_fichas RENAME TO pagos_fichas_old")
    conn.execute(new_create_sql)
    conn.execute(f"INSERT INTO pagos_fichas ({new_cols_str}) SELECT {old_cols_str} FROM pagos_fichas_old")
    conn.execute("DROP TABLE pagos_fichas_old")
    conn.commit()
    print("✓ Migración completada exitosamente.")
except Exception as e:
    conn.rollback()
    print(f"ERROR durante la migración: {e}")
    sys.exit(1)
finally:
    conn.close()

# Verificación final
conn2 = sqlite3.connect(db_path)
cur2 = conn2.cursor()
cur2.execute("PRAGMA table_info(pagos_fichas)")
cols_final = [row[1] for row in cur2.fetchall()]
print(f"Columnas finales: {cols_final}")
conn2.close()

if 'fichas' in cols_final:
    print("✓ Verificación OK: columna 'fichas' presente.")
else:
    print("ERROR: La columna 'fichas' no aparece tras la migración.")
