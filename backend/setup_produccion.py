"""
setup_produccion.py
Ejecutar UNA VEZ en PythonAnywhere para:
1. Agregar columnas goles_local y goles_visitante a la tabla partidos
2. Sincronizar fixtures.json con la DB (resultados Fecha 10)

Uso: subir este archivo a ~/sabes_de_futbol/backend/ y ejecutarlo
desde la consola Bash: python setup_produccion.py
O desde el panel Files de PythonAnywhere haciendo click en el archivo.
"""

import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'sabes_de_futbol.db')
FIXTURES_PATH = os.path.join(BASE_DIR, 'fixtures.json')

print("=" * 50)
print("SETUP PRODUCCION — Sabes de Futbol")
print("=" * 50)

# ── PASO 1: Migrar columnas ──────────────────────────
print("\n[1] Verificando columnas en tabla 'partidos'...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("PRAGMA table_info(partidos)")
cols = [r[1] for r in c.fetchall()]
print(f"    Columnas actuales: {cols}")

cambios = 0
if 'goles_local' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN goles_local INTEGER")
    print("    OK — goles_local agregado")
    cambios += 1
else:
    print("    OK — goles_local ya existe")

if 'goles_visitante' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN goles_visitante INTEGER")
    print("    OK — goles_visitante agregado")
    cambios += 1
else:
    print("    OK — goles_visitante ya existe")

if 'fecha_hora' not in cols:
    c.execute("ALTER TABLE partidos ADD COLUMN fecha_hora DATETIME")
    print("    OK — fecha_hora agregado")
    cambios += 1
else:
    print("    OK — fecha_hora ya existe")

conn.commit()
conn.close()
print(f"    {cambios} columna(s) nueva(s) agregada(s).")

# ── PASO 2: Sincronizar Fecha 10 desde fixtures.json ─
print("\n[2] Sincronizando resultados Fecha 10 desde fixtures.json...")

if not os.path.exists(FIXTURES_PATH):
    print(f"    ERROR: No se encontro {FIXTURES_PATH}")
    exit(1)

with open(FIXTURES_PATH, 'r', encoding='utf-8') as f:
    fixtures = json.load(f)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in fixtures:
    nro = item.get('nro_fecha')
    pais = item.get('pais', 'Argentina')

    # Buscar pais_id
    c.execute("SELECT id FROM paises WHERE nombre = ?", (pais,))
    row = c.fetchone()
    if not row:
        print(f"    SKIP — País '{pais}' no encontrado en DB")
        continue
    pais_id = row[0]

    # Buscar fecha_sorteo
    c.execute("SELECT id FROM fechas_sorteo WHERE nro_fecha = ? AND pais_id = ?", (nro, pais_id))
    row = c.fetchone()
    if not row:
        print(f"    SKIP — Fecha {nro} no encontrada en DB")
        continue
    fecha_id = row[0]

    partidos = item.get('partidos', [])
    # Solo procesar si son objetos enriquecidos (no strings)
    if not partidos or isinstance(partidos[0], str):
        print(f"    SKIP — Fecha {nro}: formato simple, sin resultados que cargar")
        continue

    actualizados = 0
    for idx, p in enumerate(partidos):
        if not isinstance(p, dict):
            continue

        local = p.get('local', '').strip()
        visitante = p.get('visitante', '').strip()
        resultado = p.get('resultado')
        goles_local = p.get('goles_local')
        goles_visitante = p.get('goles_visitante')
        fecha_hora_str = p.get('fecha_hora')

        fecha_hora = None
        if fecha_hora_str:
            try:
                fecha_hora = datetime.fromisoformat(fecha_hora_str)
            except ValueError:
                pass

        # Buscar el partido por nombre y fecha_id
        c.execute("""
            SELECT id FROM partidos
            WHERE fecha_sorteo_id = ? AND equipo_local = ? AND equipo_visitante = ?
        """, (fecha_id, local, visitante))
        partido_row = c.fetchone()

        if partido_row:
            c.execute("""
                UPDATE partidos
                SET resultado_real = ?, goles_local = ?, goles_visitante = ?, fecha_hora = ?
                WHERE id = ?
            """, (resultado, goles_local, goles_visitante, fecha_hora, partido_row[0]))
            actualizados += 1
        else:
            # Insertar si no existe
            c.execute("""
                INSERT INTO partidos
                (fecha_sorteo_id, equipo_local, equipo_visitante, resultado_real, orden, fecha_hora, goles_local, goles_visitante)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (fecha_id, local, visitante, resultado, idx + 1, fecha_hora, goles_local, goles_visitante))
            actualizados += 1

    conn.commit()
    print(f"    OK — Fecha {nro} ({pais}): {actualizados} partidos actualizados")

conn.close()

print("\n" + "=" * 50)
print("SETUP COMPLETADO. Hacer Reload en el panel Web.")
print("=" * 50)
