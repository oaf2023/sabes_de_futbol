
import sqlite3
import os
import sys

# Forzar el directorio actual para evitar errores de ruta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

def diagnostico():
    print(f"--- DIAGNÓSTICO DE SABES DE FUTBOL ---")
    print(f"Directorio: {BASE_DIR}")
    print(f"Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Error: La base de datos no existe en esta ruta.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Verificar tabla usuarios
        print("\nVerificando tabla 'usuarios'...")
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas = [c[1] for c in cursor.fetchall()]
        print(f"Columnas encontradas: {columnas}")
        
        if 'pais_id' not in columnas:
            print("⚠️ Falta 'pais_id'. Intentando agregar...")
            cursor.execute("ALTER TABLE usuarios ADD COLUMN pais_id INTEGER DEFAULT 1")
            print("✅ 'pais_id' agregado con éxito.")
        else:
            print("✅ 'pais_id' ya existe.")

        # 2. Verificar tabla jugadas_usuario
        print("\nVerificando tabla 'jugadas_usuario'...")
        cursor.execute("PRAGMA table_info(jugadas_usuario)")
        columnas_j = [c[1] for c in cursor.fetchall()]
        print(f"Columnas encontradas: {columnas_j}")

        if 'fecha_sorteo_id' not in columnas_j:
            print("⚠️ Falta 'fecha_sorteo_id'. Intentando agregar...")
            cursor.execute("ALTER TABLE jugadas_usuario ADD COLUMN fecha_sorteo_id INTEGER")
            print("✅ 'fecha_sorteo_id' agregado con éxito.")
        else:
            print("✅ 'fecha_sorteo_id' ya existe.")

        conn.commit()
        conn.close()
        
        # 3. Verificar modelos de Python
        print("\nVerificando modelos de SQLAlchemy (Importación)...")
        try:
            from models import Usuario
            u = Usuario()
            if hasattr(u, 'pais_id'):
                print("✅ El código de models.py ya incluye 'pais_id'.")
            else:
                print("❌ El código de models.py NO incluye 'pais_id'. ¡Debes actualizar models.py!")
        except Exception as e:
            print(f"❌ Error al importar modelos: {e}")

    except Exception as e:
        print(f"❌ Error crítico durante el diagnóstico: {e}")

    print("\n--- FIN DEL DIAGNÓSTICO ---")

if __name__ == "__main__":
    diagnostico()
