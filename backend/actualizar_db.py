
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Iniciando migración manual de la base de datos...")

    # 1. Agregar pais_id a la tabla usuarios
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN pais_id INTEGER DEFAULT 1")
        print("✅ Columna 'pais_id' agregada a la tabla 'usuarios'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ La columna 'pais_id' ya existe en 'usuarios'.")
        else:
            print(f"❌ Error al agregar 'pais_id' a 'usuarios': {e}")

    # 2. Agregar fecha_sorteo_id a la tabla jugadas_usuario
    try:
        cursor.execute("ALTER TABLE jugadas_usuario ADD COLUMN fecha_sorteo_id INTEGER")
        print("✅ Columna 'fecha_sorteo_id' agregada a la tabla 'jugadas_usuario'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ La columna 'fecha_sorteo_id' ya existe en 'jugadas_usuario'.")
        else:
            print(f"❌ Error al agregar 'fecha_sorteo_id' a 'jugadas_usuario': {e}")

    # 3. Vincular jugadas existentes con la fecha de sorteo correspondiente si es posible
    # Esto es opcional pero ayuda a que el historial funcione mejor
    try:
        # Intentamos buscar el ID de la fecha de sorteo que coincida con nro_fecha
        cursor.execute('''
            UPDATE jugadas_usuario 
            SET fecha_sorteo_id = (
                SELECT id FROM fechas_sorteo 
                WHERE fechas_sorteo.nro_fecha = jugadas_usuario.nro_fecha 
                LIMIT 1
            )
            WHERE fecha_sorteo_id IS NULL
        ''')
        print("✅ Se intentó vincular jugadas existentes con sus fechas de sorteo.")
    except Exception as e:
        print(f"ℹ️ No se pudieron vincular todas las jugadas antiguas: {e}")

    conn.commit()
    conn.close()
    print("Migración finalizada con éxito.")

if __name__ == "__main__":
    migrate()
