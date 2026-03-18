"""
Migración: agrega columna fecha_sorteo_id a jugadas_usuario si no existe.
Mantiene los datos existentes mapeando nro_fecha → fecha_sorteo_id.

Ejecutar desde: c:\\sabes_de_futbol\\backend
    python migrate_jugadas.py
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sabes_de_futbol.db')
conn = sqlite3.connect(DB)
c = conn.cursor()

# Ver columnas actuales de jugadas_usuario
c.execute("PRAGMA table_info(jugadas_usuario)")
cols = [row[1] for row in c.fetchall()]
print("Columnas actuales:", cols)

# Verificar si ya tiene fecha_sorteo_id
if 'fecha_sorteo_id' in cols:
    print("✅ La columna fecha_sorteo_id ya existe. Nada que hacer.")
    conn.close()
    exit()

# 1. Agregar columna fecha_sorteo_id (nullable por ahora)
print("Agregando columna fecha_sorteo_id...")
c.execute("ALTER TABLE jugadas_usuario ADD COLUMN fecha_sorteo_id INTEGER")

# 2. Si tiene nro_fecha, mapear a fecha_sorteo_id consultando fechas_sorteo
if 'nro_fecha' in cols:
    print("Mapeando nro_fecha → fecha_sorteo_id...")
    c.execute("SELECT id, nro_fecha FROM fechas_sorteo")
    fechas = {row[1]: row[0] for row in c.fetchall()}
    print("  fechas_sorteo disponibles:", fechas)
    
    c.execute("SELECT id, nro_fecha FROM jugadas_usuario")
    jugadas = c.fetchall()
    for jug_id, nro in jugadas:
        fecha_id = fechas.get(nro)
        if fecha_id:
            c.execute("UPDATE jugadas_usuario SET fecha_sorteo_id=? WHERE id=?", (fecha_id, jug_id))
            print(f"  Jugada {jug_id}: nro_fecha={nro} → fecha_sorteo_id={fecha_id}")
        else:
            print(f"  ⚠️ Jugada {jug_id}: nro_fecha={nro} sin match en fechas_sorteo")

conn.commit()
print("\n✅ Migración completada.")

# Verificar resultado
c.execute("SELECT id, fecha_sorteo_id FROM jugadas_usuario LIMIT 5")
print("Muestra jugadas:", c.fetchall())

conn.close()
