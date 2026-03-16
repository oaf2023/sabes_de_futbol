"""
limpiar_resultados_falsos.py

Limpia los resultados reales falsos (inventados) que quedaron guardados en la tabla 'partidos'
antes de que se implementara el fix en procesar_sorteo en la versión de producción.
Elimina los resultados donde no hay constancia de goles reales.

Ejecutar UNA VEZ localmente y en PythonAnywhere:
python limpiar_resultados_falsos.py
"""
import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Buscando resultados falsos (sin goles asignados o no correspondientes)...")

# Actualizamos a NULL donde no tenemos goles_local registrados,
# O donde goles_local y visitante son 0 pero el resultado está forzado a algo irreal
# Modificar a null los resultados que no tienen credibilidad.
c.execute('''
    UPDATE partidos 
    SET resultado_real = NULL 
    WHERE goles_local IS NULL 
       OR (goles_local = 0 AND goles_visitante = 0 AND resultado_real != 'E' AND resultado_real IS NOT NULL)
''')

# Para asegurarnos de eliminar los generados "aleatorios" que fueron 0-0 y 'E' pero sin haber iniciado la fecha
# Podemos eliminar todos los 0-0 que tengan resultado_real, asumiendo que los verdaderos 0-0
# volverán a sincronizarse correctamente con sync_resultados.py
c.execute('''
    UPDATE partidos 
    SET resultado_real = NULL 
    WHERE goles_local = 0 AND goles_visitante = 0 AND resultado_real = 'E'
''')

filas_afectadas = c.rowcount

conn.commit()
conn.close()

if filas_afectadas > 0:
    print(f"Limpieza completada.")
else:
    print("No se encontraron resultados falsos nuevos.")

print("Listo! Ya puedes probar la aplicación. No te olvides de ejecutar este script también en PythonAnywhere.")
