
import sqlite3
import os

# Forzar el directorio actual para evitar errores de ruta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'sabes_de_futbol.db')

def repair():
    print(f"--- REPARACIÓN PROFUNDA DE BASE DE DATOS ---")
    print(f"Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Error: La base de datos no existe.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def add_column(table, column, definition):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print(f"✅ Columna '{column}' agregada a '{table}'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"ℹ️ Columna '{column}' ya existe en '{table}'.")
            else:
                print(f"❌ Error en '{table}.{column}': {e}")

    # 1. Tabla Usuarios
    print("\nReparando 'usuarios'...")
    add_column('usuarios', 'fichas', 'INTEGER DEFAULT 0')
    add_column('usuarios', 'pais_id', 'INTEGER DEFAULT 1')

    # 2. Tabla jugadas_usuario
    print("\nReparando 'jugadas_usuario'...")
    add_column('jugadas_usuario', 'fecha_sorteo_id', 'INTEGER')

    # 3. Tabla pagos_fichas (La más probable de fallar ahora)
    # Si la tabla no existe, la creamos de cero. Si existe, agregamos 'pasarela'
    print("\nReparando 'pagos_fichas'...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagos_fichas'")
        if not cursor.fetchone():
            print("⚠️ Tabla 'pagos_fichas' no existe. Creándola...")
            cursor.execute('''
                CREATE TABLE pagos_fichas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_dni TEXT NOT NULL,
                    pasarela TEXT NOT NULL,
                    external_id TEXT,
                    paquete TEXT NOT NULL,
                    fichas INTEGER NOT NULL,
                    monto REAL NOT NULL,
                    moneda TEXT DEFAULT 'ARS',
                    estado TEXT DEFAULT 'pendiente',
                    fecha_creacion DATETIME,
                    fecha_resolucion DATETIME,
                    FOREIGN KEY(usuario_dni) REFERENCES usuarios(dni)
                )
            ''')
            print("✅ Tabla 'pagos_fichas' creada.")
        else:
            add_column('pagos_fichas', 'pasarela', 'TEXT')
            add_column('pagos_fichas', 'external_id', 'TEXT')
            add_column('pagos_fichas', 'paquete', 'TEXT')
            add_column('pagos_fichas', 'fichas', 'INTEGER')
            add_column('pagos_fichas', 'monto', 'REAL')
            add_column('pagos_fichas', 'moneda', "TEXT DEFAULT 'ARS'")
            add_column('pagos_fichas', 'estado', "TEXT DEFAULT 'pendiente'")
    except Exception as e:
        print(f"❌ Error con 'pagos_fichas': {e}")

    # 4. Tabla pasarelas_pago
    print("\nReparando 'pasarelas_pago'...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pasarelas_pago'")
        if not cursor.fetchone():
            print("⚠️ Tabla 'pasarelas_pago' no existe. Creándola...")
            cursor.execute('''
                CREATE TABLE pasarelas_pago (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pais_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 0,
                    config_json TEXT,
                    FOREIGN KEY(pais_id) REFERENCES paises(id)
                )
            ''')
            print("✅ Tabla 'pasarelas_pago' creada.")
    except Exception as e:
        print(f"❌ Error con 'pasarelas_pago': {e}")

    conn.commit()
    conn.close()
    print("\n--- REPARACIÓN FINALIZADA ---")
    print("IMPORTANTE: Ahora dale a RELOAD en PythonAnywhere.")

if __name__ == "__main__":
    repair()
