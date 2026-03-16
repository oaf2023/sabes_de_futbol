"""
sync_resultados.py
==================
Consulta api-football (RapidAPI) y actualiza los resultados de la fecha
activa en la DB de Sabes de Fútbol.

Configurar en backend/.env:
    RAPIDAPI_KEY=dd28eff70dmsh79872b701e54aa1p1a7df3jsn77a73a760114

Programar en PythonAnywhere → Scheduled Tasks:
    Cada 10 minutos durante los días de partido:
    /home/oaf/.virtualenvs/mi_env/bin/python /home/oaf/sabes_de_futbol/backend/sync_resultados.py

Liga Argentina Primera División: ID 135
Temporada 2025 (la API usa año de inicio del torneo)
"""

import os
import sys
import sqlite3
import requests
from datetime import datetime, timezone

# ── Cargar .env manualmente (sin depender de flask) ─────────────────────────
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

# ── Configuración ────────────────────────────────────────────────────────────
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
LEAGUE_ID    = 135        # Argentina — Primera División
SEASON       = 2025       # Año de inicio del Torneo Apertura 2026
DB_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sabes_de_futbol.db')

# Mapeo nombre API → nombre en tu DB
# Ajustar si hay diferencias después de ver la respuesta real
NOMBRES = {
    'Tigre':                    'Tigre',
    'Velez Sarsfield':          'Vélez',
    'Independiente':            'Independiente',
    'Union Santa Fe':           'Unión',
    'Sarmiento':                'Sarmiento',
    'Racing Club':              'Racing',
    "Newell's Old Boys":        "Newell's",
    'Platense':                 'Platense',
    'Banfield':                 'Banfield',
    'Gimnasia LP':              'Gimnasia',
    'Argentinos Juniors':       'Argentinos',
    'Rosario Central':          'Rosario Central',
    'Boca Juniors':             'Boca',
    'San Lorenzo':              'San Lorenzo',
    'Independiente Rivadavia':  'Ind. Rivadavia Mza.',
    'Barracas Central':         'Barracas Central',
    'Atletico Tucuman':         'Atlético Tucumán',
    'Aldosivi':                 'Aldosivi',
    'Deportivo Riestra':        'Riestra',
    'Gimnasia Mendoza':         'Gimnasia (Mza.)',
    'Defensa y Justicia':       'Defensa y Justicia',
    'Central Cordoba':          'Central Córdoba',
    'Talleres Cordoba':         'Talleres',
    'Instituto':                'Instituto',
    'Estudiantes RC':           'Estudiantes (RC)',
    'Belgrano':                 'Belgrano',
    'Huracan':                  'Huracán',
    'River Plate':              'River',
    'Estudiantes':              'Estudiantes',
    'Lanus':                    'Lanús',
}

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] {msg}', flush=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_fecha_activa(conn):
    row = conn.execute(
        'SELECT fa.nro_fecha, fs.id as fs_id FROM fecha_actual fa '
        'JOIN fechas_sorteo fs ON fs.nro_fecha = fa.nro_fecha AND fs.pais_id = fa.pais_id '
        'WHERE fa.activo = 1 AND fa.pais_id = 1 LIMIT 1'
    ).fetchone()
    return row

def fetch_fixtures(round_label=None):
    """Trae todos los partidos de la liga/temporada. Filtra por round si se indica."""
    url = 'https://sportapi7.p.rapidapi.com/api/v2/matches'
    params = {
        'league': LEAGUE_ID,
        'season': SEASON,
    }
    if round_label:
        params['round'] = round_label

    headers = {
        'x-rapidapi-key':  RAPIDAPI_KEY,
        'x-rapidapi-host': 'sportapi7.p.rapidapi.com'
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data.get('errors'):
        log(f'API error: {data["errors"]}')
        return []

    return data.get('response', [])

def resolver_resultado(home_goals, away_goals):
    if home_goals is None or away_goals is None:
        return None
    if home_goals > away_goals:
        return 'L'
    elif home_goals < away_goals:
        return 'V'
    return 'E'

def normalizar(nombre_api):
    """Busca en el mapa, si no encuentra devuelve el nombre tal cual."""
    return NOMBRES.get(nombre_api, nombre_api)

def sync():
    if not RAPIDAPI_KEY:
        log('ERROR: RAPIDAPI_KEY no configurada en .env')
        sys.exit(1)

    log('=== Iniciando sync_resultados ===')

    conn = get_db()
    fecha = get_fecha_activa(conn)

    if not fecha:
        log('No hay fecha activa. Saliendo.')
        conn.close()
        return

    nro_fecha = fecha['nro_fecha']
    fs_id     = fecha['fs_id']
    log(f'Fecha activa: #{nro_fecha:05d} (fs_id={fs_id})')

    # Traer partidos de la DB para esta fecha
    db_partidos = conn.execute(
        'SELECT id, equipo_local, equipo_visitante, resultado_real '
        'FROM partidos WHERE fecha_sorteo_id = ? ORDER BY orden',
        (fs_id,)
    ).fetchall()

    if not db_partidos:
        log('No hay partidos en la DB para esta fecha.')
        conn.close()
        return

    # Construir el label del round que usa la API  (ej: "Regular Season - 10")
    round_label = f'Regular Season - {nro_fecha}'
    log(f'Consultando API: league={LEAGUE_ID} season={SEASON} round="{round_label}"')

    try:
        fixtures = fetch_fixtures(round_label)
    except requests.RequestException as e:
        log(f'ERROR consultando API: {e}')
        conn.close()
        return

    if not fixtures:
        log(f'La API no devolvió partidos para round "{round_label}". '
            f'Verificar si el round label es correcto.')
        conn.close()
        return

    log(f'API devolvió {len(fixtures)} partidos.')

    # Indexar fixtures de la API por (local_norm, visita_norm)
    api_index = {}
    for f in fixtures:
        home = f['teams']['home']['name']
        away = f['teams']['away']['name']
        api_index[(normalizar(home), normalizar(away))] = f

    actualizados = 0
    no_encontrados = []

    for p in db_partidos:
        key = (p['equipo_local'], p['equipo_visitante'])
        fixture = api_index.get(key)

        if not fixture:
            no_encontrados.append(f"{p['equipo_local']} vs {p['equipo_visitante']}")
            continue

        status    = fixture['fixture']['status']['short']  # FT, NS, 1H, 2H, HT, etc.
        home_g    = fixture['goals']['home']
        away_g    = fixture['goals']['away']
        resultado = resolver_resultado(home_g, away_g) if status == 'FT' else None

        # Solo actualizar si hay cambio
        if (fixture['goals']['home'] != p['resultado_real'] or
            home_g is not None):

            conn.execute(
                'UPDATE partidos SET goles_local=?, goles_visitante=?, resultado_real=? WHERE id=?',
                (home_g, away_g, resultado, p['id'])
            )
            actualizados += 1
            estado_str = f'{home_g}-{away_g} ({status})'
            log(f'  ✓ {p["equipo_local"]} vs {p["equipo_visitante"]}: {estado_str}')

    conn.commit()
    conn.close()

    log(f'Actualizados: {actualizados} partidos.')
    if no_encontrados:
        log(f'SIN MAPEO (revisar NOMBRES): {no_encontrados}')
        log('  → Agregá los nombres faltantes al dict NOMBRES en este script.')

    log('=== Sync completado ===')

if __name__ == '__main__':
    sync()
