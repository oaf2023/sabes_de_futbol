import sqlite3

conn = sqlite3.connect(r'backend/sabes_de_futbol.db')
c = conn.cursor()

print('=== TABLAS ===')
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(c.fetchall())

print('\n=== FECHAS_SORTEO ===')
c.execute('SELECT id, nro_fecha, pais_id FROM fechas_sorteo')
print(c.fetchall())

print('\n=== FECHA_ACTUAL ===')
try:
    c.execute('SELECT * FROM fecha_actual')
    print(c.fetchall())
except Exception as e:
    print('No existe:', e)

print('\n=== PARTIDOS esquema ===')
c.execute('PRAGMA table_info(partidos)')
print(c.fetchall())

print('\n=== PARTIDOS (primeros 3) ===')
c.execute('SELECT id, fecha_sorteo_id, equipo_local FROM partidos LIMIT 3')
print(c.fetchall())

print('\n=== USUARIOS ===')
c.execute('SELECT dni, nombre, fichas FROM usuarios')
print(c.fetchall())

conn.close()
