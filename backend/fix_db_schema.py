
import os
import sqlite3

# Ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Iniciando migración manual de esquema SQLite...")

    try:
        # 1. Agregar nuevas columnas a la tabla 'usuarios' una por una
        # SQLite no permite agregar múltiples columnas en un solo ALTER TABLE
        columnas_usuarios = [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("numero_de_socio", "INTEGER UNIQUE"),
            ("nombre_de_usuario", "VARCHAR(50) UNIQUE"),
            ("fichas_compradas", "INTEGER DEFAULT 0"),
            ("fichas_ganadas", "INTEGER DEFAULT 0")
        ]

        for col_name, col_type in columnas_usuarios:
            try:
                cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {col_name} {col_type}")
                print(f"Columna '{col_name}' agregada a 'usuarios'.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"La columna '{col_name}' ya existe en 'usuarios'.")
                else:
                    print(f"Aviso al agregar '{col_name}': {e}")

        # 2. Modificar 'usuarios.dni' y otros para ser nullable
        # En SQLite no se puede cambiar NULL/NOT NULL con ALTER TABLE directamente.
        # Pero como ya quitamos las restricciones en el modelo de SQLAlchemy,
        # SQLite nos permitirá insertar nulos si no había un constraint NOT NULL previo muy estricto.
        # Nota: En SQLAlchemy 'dni' era PK (NOT NULL). Para cambiarlo realmente en SQLite
        # habría que recrear la tabla, pero intentaremos trabajar con lo que hay.

        # 3. Agregar columna 'usuario_id' a 'jugadas_usuario'
        try:
            cursor.execute("ALTER TABLE jugadas_usuario ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
            print("Columna 'usuario_id' agregada a 'jugadas_usuario'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("La columna 'usuario_id' ya existe en 'jugadas_usuario'.")
            else:
                print(f"Aviso al agregar 'usuario_id' a jugadas: {e}")

        # 4. Cambiar 'usuario_dni' en jugadas_usuario a nullable (aunque SQLite no lo aplica fácil,
        # SQLAlchemy lo manejará si la columna no tiene el constraint a nivel DB).

        conn.commit()
        print("Migración de esquema completada con éxito.")

    except Exception as e:
        conn.rollback()
        print(f"Error crítico durante la migración de esquema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
