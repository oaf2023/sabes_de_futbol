"""
limpiar_aciertos_viejos.py
Pone en NULL los aciertos de jugadas de fechas anteriores a la activa,
ya que fueron calculados con resultados aleatorios (no reales).
Ejecutar UNA VEZ en PythonAnywhere: python limpiar_aciertos_viejos.py
"""
import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Ver estado actual
c.execute('SELECT id, usuario_dni, nro_fecha, aciertos FROM jugadas_usuario ORDER BY id DESC')
jugadas = c.fetchall()
print(f'Total jugadas: {len(jugadas)}')
for j in jugadas:
    print(f'  id={j[0]} | dni={j[1]} | fecha={j[2]} | aciertos={j[3]}')

# Ver fecha activa
c.execute('SELECT nro_fecha FROM fecha_actual WHERE activo=1 LIMIT 1')
row = c.fetchone()
fecha_activa = row[0] if row else None
print(f'\nFecha activa: {fecha_activa}')

# Limpiar aciertos de fechas ANTERIORES a la activa
if fecha_activa:
    c.execute(
        'UPDATE jugadas_usuario SET aciertos = NULL WHERE nro_fecha < ?',
        (fecha_activa,)
    )
    print(f'Limpiadas {c.rowcount} jugadas de fechas anteriores a {fecha_activa}.')
else:
    print('No hay fecha activa, limpiando TODOS los aciertos...')
    c.execute('UPDATE jugadas_usuario SET aciertos = NULL')
    print(f'Limpiadas {c.rowcount} jugadas.')

conn.commit()

# Verificar
c.execute('SELECT id, usuario_dni, nro_fecha, aciertos FROM jugadas_usuario ORDER BY id DESC')
print('\nEstado final:')
for j in c.fetchall():
    print(f'  id={j[0]} | dni={j[1]} | fecha={j[2]} | aciertos={j[3]}')

conn.close()
print('\nListo. Hacer Reload en el panel Web.')
