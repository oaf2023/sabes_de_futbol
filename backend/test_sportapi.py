"""
test_sportapi.py
Prueba la conexión con SportAPI y muestra la estructura de respuesta.
Ejecutar: python test_sportapi.py
"""
import os
import json
import requests

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

KEY  = os.getenv('RAPIDAPI_KEY', '')
HOST = 'sportapi7.p.rapidapi.com'
HEADERS = {
    'x-rapidapi-key':  KEY,
    'x-rapidapi-host': HOST
}

def probar(descripcion, url, params={}):
    print(f'\n{"="*60}')
    print(f'TEST: {descripcion}')
    print(f'URL:  {url}')
    print(f'PARAMS: {params}')
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        print(f'STATUS: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        else:
            print(r.text[:500])
    except Exception as e:
        print(f'ERROR: {e}')

BASE = f'https://{HOST}'
from datetime import date
hoy = date.today().isoformat()

# ── Buscar torneos de Argentina en eventos de hoy ────────────────────────────
print(f'\n{"="*60}')
print(f'TEST: Buscar Argentina en scheduled-events de hoy ({hoy})')
url = f'{BASE}/api/v1/sport/football/scheduled-events/{hoy}'
try:
    r = requests.get(url, headers=HEADERS, timeout=15)
    print(f'STATUS: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        eventos = data.get('events', [])
        print(f'Total eventos: {len(eventos)}')
        argentina = {}
        for e in eventos:
            cat = e.get('tournament', {}).get('category', {}).get('name', '')
            if 'argentina' in cat.lower():
                tid  = e.get('tournament', {}).get('uniqueTournament', {}).get('id', '?')
                tnm  = e.get('tournament', {}).get('uniqueTournament', {}).get('name', '?')
                slug = e.get('tournament', {}).get('uniqueTournament', {}).get('slug', '?')
                key = (tid, tnm, slug)
                if key not in argentina:
                    argentina[key] = 0
                argentina[key] += 1
        if argentina:
            print('\nTorneos de Argentina encontrados:')
            for (tid, tnm, slug), cnt in sorted(argentina.items()):
                print(f'  uniqueTournament.id={tid}  name="{tnm}"  slug="{slug}"  partidos={cnt}')
        else:
            print('No se encontraron eventos de Argentina hoy.')
            # Mostrar categorías disponibles para debug
            cats = {}
            for e in eventos:
                cat = e.get('tournament', {}).get('category', {}).get('name', 'N/A')
                cats[cat] = cats.get(cat, 0) + 1
            print('Categorías disponibles (primeras 20):')
            for cat, cnt in sorted(cats.items())[:20]:
                print(f'  {cat}: {cnt}')
    else:
        print(r.text[:500])
except Exception as e:
    print(f'ERROR: {e}')

# ── Buscar por nombre "Argentina" en search endpoint ─────────────────────────
probar('search unique-tournament argentina', f'{BASE}/api/v1/unique-tournament/search', {'q': 'Argentina Primera'})

# ── Info de torneos candidatos (IDs conocidos de SofaScore para Argentina) ───
for tid in [703, 704, 730, 1669, 13475]:
    probar(f'info torneo {tid}', f'{BASE}/api/v1/unique-tournament/{tid}', {})
