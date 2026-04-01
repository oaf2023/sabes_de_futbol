
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

def recreate_users_table():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Recreando tabla 'usuarios' para soportar el nuevo esquema...")

    try:
        # 1. Crear tabla temporal con el esquema nuevo
        # Nota: He incluido todas las columnas del modelo de SQLAlchemy
        cursor.execute("""
            CREATE TABLE usuarios_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_de_socio INTEGER UNIQUE,
                nombre_de_usuario VARCHAR(50) UNIQUE,
                dni VARCHAR(20),
                telefono VARCHAR(30),
                email VARCHAR(120),
                direccion VARCHAR(200),
                nombre VARCHAR(100),
                fecha_nac VARCHAR(20),
                password_hash VARCHAR(256) NOT NULL,
                foto_dni_frente VARCHAR(300),
                foto_dni_dorso VARCHAR(300),
                foto_selfie VARCHAR(300),
                fecha_registro DATETIME,
                fichas INTEGER DEFAULT 0,
                fichas_compradas INTEGER DEFAULT 0,
                fichas_ganadas INTEGER DEFAULT 0,
                pais_id INTEGER REFERENCES paises(id),
                completado VARCHAR(2) DEFAULT 'NO'
            )
        """)

        # 2. Copiar datos de la tabla vieja a la nueva
        # Mapeamos las columnas existentes. Las nuevas quedarán en NULL por ahora.
        cursor.execute("""
            INSERT INTO usuarios_new (
                dni, telefono, email, direccion, nombre, fecha_nac, 
                password_hash, foto_dni_frente, foto_dni_dorso, foto_selfie, 
                fecha_registro, fichas, pais_id, completado
            )
            SELECT 
                dni, telefono, email, direccion, nombre, fecha_nac, 
                password_hash, foto_dni_frente, foto_dni_dorso, foto_selfie, 
                fecha_registro, fichas, pais_id, completado
            FROM usuarios
        """)

        # 3. Eliminar tabla vieja y renombrar la nueva
        cursor.execute("DROP TABLE usuarios")
        cursor.execute("ALTER TABLE usuarios_new RENAME TO usuarios")

        # 4. Asegurar que jugadas_usuario tiene la columna usuario_id
        try:
            cursor.execute("ALTER TABLE jugadas_usuario ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
            print("Columna 'usuario_id' agregada a 'jugadas_usuario'.")
        except sqlite3.OperationalError:
            print("La columna 'usuario_id' ya existía en 'jugadas_usuario'.")

        conn.commit()
        print("Esquema de tabla 'usuarios' actualizado correctamente.")

    except Exception as e:
        conn.rollback()
        print(f"Error crítico: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    recreate_users_table()
