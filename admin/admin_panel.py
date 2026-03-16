"""
admin_panel.py — Panel de Administración Sabes de Fútbol
Conecta a la API de producción en PythonAnywhere via HTTP.

Uso:
    streamlit run admin_panel.py

Requiere admin/.env:
    API_BASE=https://www.sabesdefutbol.com
    ADMIN_SECRET=tu_clave_admin
    ADMIN_PASSWORD=clave_para_entrar_al_panel
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_BASE     = os.getenv('API_BASE', 'https://www.sabesdefutbol.com').rstrip('/')
ADMIN_SECRET = os.getenv('ADMIN_SECRET', '')
ADMIN_PASS   = os.getenv('ADMIN_PASSWORD', 'admin1234')

st.set_page_config(
    page_title="Admin — Sabes de Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=VT323&display=swap');
    html, body, [class*="css"] { font-family: 'Courier New', monospace; }
    h1, h2, h3 { font-family: 'Special Elite', cursive !important; color: #1a5276 !important; }
    .stButton > button {
        background: #1a5276; color: white; border: none;
        font-family: 'Special Elite', cursive; letter-spacing: 1px;
    }
    .stButton > button:hover { background: #27ae60; }
    .metric-box {
        background: #1a5276; color: white; border-radius: 8px;
        padding: 12px 16px; text-align: center;
    }
    .metric-box .val { font-family: 'VT323', monospace; font-size: 2.5rem; color: #f0e68c; }
    .metric-box .lbl { font-size: 0.75rem; letter-spacing: 2px; opacity: 0.8; }
    .tag-si  { background:#27ae60; color:white; padding:2px 8px; border-radius:4px; font-size:0.8rem; }
    .tag-no  { background:#922b21; color:white; padding:2px 8px; border-radius:4px; font-size:0.8rem; }
    .tag-fin { background:#1a5276; color:#f0e68c; padding:2px 8px; border-radius:4px; font-size:0.8rem; }
    .tag-pend{ background:#e67e22; color:white; padding:2px 8px; border-radius:4px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTENTICACIÓN LOCAL
# ─────────────────────────────────────────────
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("## ⚽ SABES DE FÚTBOL — Panel Admin")
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        clave = st.text_input("Contraseña de administrador", type="password")
        if st.button("INGRESAR", use_container_width=True):
            if clave == ADMIN_PASS:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

# ─────────────────────────────────────────────
# CLIENTE HTTP
# ─────────────────────────────────────────────
HEADERS = {'X-Admin-Secret': ADMIN_SECRET}

def api_get(path, params=None):
    try:
        r = requests.get(f'{API_BASE}{path}', headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.HTTPError as e:
        return None, f'HTTP {e.response.status_code}: {e.response.text[:200]}'
    except Exception as e:
        return None, str(e)

def api_post(path, body=None):
    try:
        r = requests.post(f'{API_BASE}{path}', headers={**HEADERS, 'Content-Type': 'application/json'},
                          json=body, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.HTTPError as e:
        return None, f'HTTP {e.response.status_code}: {e.response.text[:200]}'
    except Exception as e:
        return None, str(e)

def api_delete(path):
    try:
        r = requests.delete(f'{API_BASE}{path}', headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.HTTPError as e:
        return None, f'HTTP {e.response.status_code}: {e.response.text[:200]}'
    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚽ SABES DE FÚTBOL")
    st.markdown("**Panel de Administración**")
    st.markdown("---")
    seccion = st.radio("Sección", [
        "📊 Dashboard",
        "📅 Fechas & Fixture",
        "⚽ Resultados",
        "👥 Socios",
        "🪙 Fichas",
        "💳 Pagos",
    ])
    st.markdown("---")
    st.caption(f"API: `{API_BASE}`")
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

# ══════════════════════════════════════════════
# 1. DASHBOARD
# ══════════════════════════════════════════════
if seccion == "📊 Dashboard":
    st.title("📊 Dashboard")

    data, err = api_get('/api/admin/stats')
    if err:
        st.error(f"Error al conectar con la API: {err}")
        st.stop()

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, lbl in [
        (c1, data['socios'],       "SOCIOS"),
        (c2, data['completos'],    "COMPLETOS"),
        (c3, data['jugadas'],      "JUGADAS"),
        (c4, data['fichas_total'], "FICHAS EN JUEGO"),
        (c5, data['pagos_ok'],     "PAGOS OK"),
    ]:
        col.markdown(f"""
        <div class="metric-box">
            <div class="val">{val}</div>
            <div class="lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Últimos socios registrados")
        for s in data.get('ultimos_socios', []):
            tag = '<span class="tag-si">COMPLETO</span>' if s.get('completado') == 'SI' else '<span class="tag-no">INCOMPLETO</span>'
            st.markdown(f"**{s.get('nombre') or '—'}** `{s['dni']}` {tag}", unsafe_allow_html=True)

    with col_b:
        st.subheader("Fecha activa por país")
        for fa in data.get('fechas_activas', []):
            estado = "🟢 Activa" if fa['activo'] else "🔴 Inactiva"
            st.markdown(f"**{fa['pais']}** — Fecha `#{fa['nro_fecha']:05d}` {estado}")

    st.markdown("---")
    st.subheader("Últimas jugadas")
    jugadas, _ = api_get('/api/admin/jugadas')
    if jugadas:
        import pandas as pd
        df = pd.DataFrame(jugadas)
        st.dataframe(df, use_container_width=True)

# ══════════════════════════════════════════════
# 2. FECHAS & FIXTURE
# ══════════════════════════════════════════════
elif seccion == "📅 Fechas & Fixture":
    st.title("📅 Fechas & Fixture")

    paises_data, err = api_get('/api/admin/paises')
    if err:
        st.error(err)
        st.stop()

    # ── Estado de sesión para alternar entre fecha activa y próxima ──
    if 'viendo_proxima' not in st.session_state:
        st.session_state.viendo_proxima = False

    # Obtener país y fecha activa para el selector de próxima fecha
    p_nombres_global = {p['nombre']: p['id'] for p in paises_data}
    pais_sel_global  = st.selectbox("País", list(p_nombres_global.keys()), key="pais_global")
    pais_id_global   = p_nombres_global[pais_sel_global]

    fechas_global, _ = api_get('/api/admin/fechas', {'pais_id': pais_id_global})
    fa_global, _     = api_get('/api/admin/fecha-activa', {'pais_id': pais_id_global})
    nro_activo       = fa_global[0]['nro_fecha'] if fa_global else None
    nro_proximo      = nro_activo + 1 if nro_activo else None
    proxima_existe   = any(f['nro_fecha'] == nro_proximo for f in (fechas_global or []))

    # ── Botones para alternar vista ──
    if nro_activo:
        st.markdown("---")
        col_act, col_prox = st.columns(2)
        with col_act:
            if st.button(
                f"📅 FECHA ACTIVA #{nro_activo:05d}",
                use_container_width=True,
                disabled=not st.session_state.viendo_proxima
            ):
                st.session_state.viendo_proxima = False
                st.rerun()
        with col_prox:
            label_prox = f"📆 PRÓXIMA FECHA #{nro_proximo:05d}" + (" ✓" if proxima_existe else " (nueva)")
            if st.button(label_prox, use_container_width=True, disabled=st.session_state.viendo_proxima):
                st.session_state.viendo_proxima = True
                st.rerun()

        # ── Banner informativo ──
        if st.session_state.viendo_proxima:
            if proxima_existe:
                st.info(f"📆 Editando Fecha **#{nro_proximo:05d}** — aún no activada. Podés cargar partidos y resultados anticipados.")
            else:
                st.warning(f"📆 Fecha **#{nro_proximo:05d}** no existe todavía. Creala desde el tab **Nueva Fecha**.")
        else:
            st.info(f"📅 Viendo Fecha activa **#{nro_activo:05d}**")
        st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Activar Fecha", "Ver Fixture", "Nueva Fecha"])

    # ── Activar Fecha ──
    with tab1:
        st.subheader("Activar fecha por país")
        p_nombres = {p['nombre']: p['id'] for p in paises_data}
        pais_id   = pais_id_global

        fechas, _ = api_get('/api/admin/fechas', {'pais_id': pais_id})
        if not fechas:
            st.warning("No hay fechas para este país.")
        else:
            nros    = [f['nro_fecha'] for f in fechas]
            # Pre-seleccionar próxima fecha si estamos en ese modo
            default_idx = len(nros) - 1
            if st.session_state.viendo_proxima and nro_proximo and nro_proximo in nros:
                default_idx = nros.index(nro_proximo)
            nro_sel = st.selectbox("Número de fecha a activar", nros, index=default_idx)

            if fa_global:
                st.info(f"Fecha activa actual: **#{fa_global[0]['nro_fecha']:05d}**")

            if st.button("✅ Activar esta fecha", use_container_width=True):
                res, err = api_post('/api/admin/activar-fecha', {'pais_id': pais_id, 'nro_fecha': nro_sel})
                if err:
                    st.error(err)
                else:
                    st.success(f"✅ Fecha #{nro_sel:05d} activada para {pais_sel_global}")
                    st.session_state.viendo_proxima = False
                    st.rerun()

    # ── Ver Fixture ──
    with tab2:
        st.subheader("Consultar fixture de una fecha")
        pais_id2   = pais_id_global
        fechas2, _ = api_get('/api/admin/fechas', {'pais_id': pais_id2})
        if not fechas2:
            st.warning("No hay fechas para este país.")
        else:
            nros2 = [f['nro_fecha'] for f in fechas2]
            # Pre-seleccionar próxima o activa según el modo
            default_idx2 = len(nros2) - 1
            if st.session_state.viendo_proxima and nro_proximo and nro_proximo in nros2:
                default_idx2 = nros2.index(nro_proximo)
            elif not st.session_state.viendo_proxima and nro_activo and nro_activo in nros2:
                default_idx2 = nros2.index(nro_activo)
            nro_sel2 = st.selectbox("Fecha", nros2, index=default_idx2, key="nro_fix")
            data2, _ = api_get('/api/admin/partidos', {'pais_id': pais_id2, 'nro_fecha': nro_sel2})
            if data2 and data2.get('partidos'):
                partidos2 = data2['partidos']
                st.caption(f"{len(partidos2)} partidos en la DB")

                for p in partidos2:
                    marcador = f"{p['goles_local']} - {p['goles_visitante']}" if p['goles_local'] is not None else "—"
                    res_str  = p['resultado'] or 'PEND'
                    col_info, col_del = st.columns([10, 1])
                    with col_info:
                        st.markdown(
                            f"`#{p['id']}` **{p['local']} vs {p['visitante']}** — {marcador} [{res_str}] "
                            f"<small>{p.get('fecha_hora','') or ''}</small>",
                            unsafe_allow_html=True
                        )
                    with col_del:
                        if st.button("🗑", key=f"del_{p['id']}", help=f"Eliminar partido #{p['id']}"):
                            _, err = api_delete(f"/api/admin/partido/{p['id']}")
                            if err:
                                st.error(err)
                            else:
                                st.success(f"Partido #{p['id']} eliminado.")
                                st.rerun()
            else:
                st.info("Esta fecha no tiene partidos cargados.")

    # ── Nueva Fecha ──
    with tab3:
        st.subheader("Crear nueva fecha con partidos")
        st.caption("Ingresá un partido por línea: **Local vs Visitante | YYYY-MM-DD HH:MM**")
        pais_id3    = pais_id_global
        # Pre-completar el número si estamos en modo próxima y no existe aún
        nro_default = int(nro_proximo) if (st.session_state.viendo_proxima and nro_proximo and not proxima_existe) else 1
        nro_nuevo   = st.number_input("Número de fecha", min_value=1, step=1, value=nro_default)
        partidos_txt = st.text_area("Partidos (uno por línea)", height=300,
            placeholder="Boca vs River | 2026-03-20 20:00\nRacing vs Independiente | 2026-03-20 22:00")

        if st.button("💾 Crear fecha", use_container_width=True):
            lineas = [l.strip() for l in partidos_txt.strip().splitlines() if l.strip()]
            if not lineas:
                st.error("Ingresá al menos un partido.")
            else:
                partidos_list = []
                errores = []
                for idx, linea in enumerate(lineas):
                    partes = linea.split('|')
                    match  = partes[0].strip()
                    fh_str = partes[1].strip() if len(partes) > 1 else None
                    if ' vs ' not in match:
                        errores.append(f"Línea {idx+1}: formato inválido")
                        continue
                    local, visita = match.split(' vs ', 1)
                    fh = None
                    if fh_str:
                        try:
                            fh = datetime.strptime(fh_str, '%Y-%m-%d %H:%M').isoformat()
                        except:
                            errores.append(f"Línea {idx+1}: fecha inválida '{fh_str}'")
                    partidos_list.append({'local': local.strip(), 'visitante': visita.strip(), 'fecha_hora': fh})

                res, err = api_post('/api/admin/nueva-fecha', {
                    'pais_id': pais_id3, 'nro_fecha': int(nro_nuevo), 'partidos': partidos_list
                })
                for e in errores:
                    st.warning(e)
                if err:
                    st.error(err)
                else:
                    st.success(f"✅ Fecha #{int(nro_nuevo)} creada con {len(partidos_list)} partidos.")
                    st.rerun()

# ══════════════════════════════════════════════
# 3. RESULTADOS
# ══════════════════════════════════════════════
elif seccion == "⚽ Resultados":
    st.title("⚽ Cargar Resultados")

    paises_data, err = api_get('/api/admin/paises')
    if err:
        st.error(err)
        st.stop()

    p_nombres = {p['nombre']: p['id'] for p in paises_data}
    pais_sel  = st.selectbox("País", list(p_nombres.keys()))
    pais_id   = p_nombres[pais_sel]

    fa, _ = api_get('/api/admin/fecha-activa', {'pais_id': pais_id})
    nro_activo_res = fa[0]['nro_fecha'] if (fa and fa[0].get('activo')) else None

    # Permitir cargar resultados de fecha activa o próxima
    fechas_res, _ = api_get('/api/admin/fechas', {'pais_id': pais_id})
    nros_res = [f['nro_fecha'] for f in (fechas_res or [])]

    if not nros_res:
        st.warning("No hay fechas para este país.")
        st.stop()

    default_res = len(nros_res) - 1
    if nro_activo_res and nro_activo_res in nros_res:
        default_res = nros_res.index(nro_activo_res)

    nro_fecha = st.selectbox("Fecha a cargar resultados", nros_res, index=default_res, key="nro_res")

    if nro_activo_res and nro_fecha == nro_activo_res:
        st.caption("📅 Fecha activa")
    elif nro_activo_res and nro_fecha == nro_activo_res + 1:
        st.caption("📆 Próxima fecha — carga anticipada")

    data, err = api_get('/api/admin/partidos', {'pais_id': pais_id, 'nro_fecha': nro_fecha})
    if err or not data or not data.get('partidos'):
        st.warning("Esta fecha no tiene fixture cargado. Creá los partidos en '📅 Fechas & Fixture'.")
        st.stop()

    st.markdown(f"### Fecha #{nro_fecha:05d} — {pais_sel}")
    st.markdown("---")

    RESULTADO_OPTS = {"— Sin resultado —": None, "Local (L)": "L", "Empate (E)": "E", "Visitante (V)": "V"}
    partidos = data['partidos']

    with st.form("form_resultados"):
        cambios = []
        for p in partidos:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
            with col1:
                st.markdown(f"**{p['local']} vs {p['visitante']}**")
            with col2:
                gl = st.number_input("G.L", min_value=0, max_value=99, step=1,
                    value=int(p['goles_local']) if p['goles_local'] is not None else 0,
                    key=f"gl_{p['id']}", label_visibility="collapsed")
            with col3:
                gv = st.number_input("G.V", min_value=0, max_value=99, step=1,
                    value=int(p['goles_visitante']) if p['goles_visitante'] is not None else 0,
                    key=f"gv_{p['id']}", label_visibility="collapsed")
            with col4:
                res_actual = p['resultado']
                res_label  = next((k for k, v in RESULTADO_OPTS.items() if v == res_actual), "— Sin resultado —")
                res_sel    = st.selectbox("Resultado", list(RESULTADO_OPTS.keys()),
                    index=list(RESULTADO_OPTS.keys()).index(res_label),
                    key=f"res_{p['id']}", label_visibility="collapsed")
            with col5:
                if p['resultado']:
                    st.markdown('<span class="tag-fin">FIN</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="tag-pend">PEND</span>', unsafe_allow_html=True)

            cambios.append({'partido_id': p['id'], 'goles_local': gl, 'goles_visitante': gv,
                            'resultado': RESULTADO_OPTS[res_sel]})

        submitted = st.form_submit_button("💾 GUARDAR RESULTADOS", use_container_width=True)

    if submitted:
        errores = []
        for c in cambios:
            _, err = api_post('/api/admin/resultado', c)
            if err:
                errores.append(err)
        if errores:
            for e in errores:
                st.error(e)
        else:
            st.success(f"✅ {len(cambios)} partidos actualizados en producción.")
            st.rerun()

# ══════════════════════════════════════════════
# 4. SOCIOS
# ══════════════════════════════════════════════
elif seccion == "👥 Socios":
    st.title("👥 Gestión de Socios")

    tab1, tab2 = st.tabs(["Ver Socios", "Editar Socio"])

    with tab1:
        st.subheader("Listado de socios")
        filtro = st.text_input("Buscar por DNI o nombre")
        socios, err = api_get('/api/admin/socios', {'q': filtro} if filtro else None)
        if err:
            st.error(err)
        else:
            st.caption(f"{len(socios)} socios encontrados")
            import pandas as pd
            if socios:
                st.dataframe(pd.DataFrame(socios), use_container_width=True)

    with tab2:
        st.subheader("Editar datos de un socio")
        dni_edit = st.text_input("DNI del socio a editar")
        if dni_edit:
            socio, err = api_get(f'/api/admin/socio/{dni_edit}')
            if err:
                st.error("Socio no encontrado.")
            else:
                with st.form("form_socio"):
                    nombre   = st.text_input("Nombre",    value=socio.get('nombre') or '')
                    email    = st.text_input("Email",     value=socio.get('email') or '')
                    telefono = st.text_input("Teléfono",  value=socio.get('telefono') or '')
                    fichas   = st.number_input("Fichas",  min_value=0, value=int(socio.get('fichas') or 0))
                    completo = st.selectbox("Completado", ["SI", "NO"],
                                            index=0 if socio.get('completado') == 'SI' else 1)
                    nueva_pass = st.text_input("Nueva contraseña (dejar vacío para no cambiar)", type="password")
                    if st.form_submit_button("💾 Guardar cambios"):
                        body = {'nombre': nombre, 'email': email, 'telefono': telefono,
                                'fichas': fichas, 'completado': completo}
                        if nueva_pass.strip():
                            body['nueva_password'] = nueva_pass.strip()
                        _, err = api_post(f'/api/admin/socio/{dni_edit}', body)
                        if err:
                            st.error(err)
                        else:
                            st.success("✅ Socio actualizado.")

# ══════════════════════════════════════════════
# 5. FICHAS
# ══════════════════════════════════════════════
elif seccion == "🪙 Fichas":
    st.title("🪙 Gestión de Fichas")

    tab1, tab2 = st.tabs(["Acreditar Fichas", "Historial"])

    with tab1:
        st.subheader("Acreditar fichas manualmente")
        col1, col2 = st.columns(2)
        with col1:
            dni_fichas = st.text_input("DNI del socio")
        with col2:
            cant = st.number_input("Fichas a acreditar", min_value=1, max_value=500, value=5)
        motivo = st.selectbox("Motivo", ["Pago confirmado", "Bonificación", "Corrección", "Premio", "Otro"])
        nota   = st.text_input("Nota adicional (opcional)")

        if st.button("🪙 ACREDITAR FICHAS", use_container_width=True):
            if not dni_fichas:
                st.error("Ingresá un DNI.")
            else:
                res, err = api_post('/api/admin/acreditar-fichas', {
                    'dni': dni_fichas, 'cantidad': cant, 'motivo': f'{motivo} {nota}'.strip()
                })
                if err:
                    st.error(err)
                else:
                    st.success(f"✅ Fichas acreditadas. Total ahora: **{res['fichas_nuevas']}**")

    with tab2:
        st.subheader("Últimas acreditaciones")
        pagos, err = api_get('/api/admin/pagos', {'estado': 'aprobado'})
        if err:
            st.error(err)
        elif pagos:
            import pandas as pd
            df = pd.DataFrame(pagos)
            cols = [c for c in ['id','usuario_dni','nombre','paquete','fichas','monto','pasarela','fecha_creacion'] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

# ══════════════════════════════════════════════
# 6. PAGOS
# ══════════════════════════════════════════════
elif seccion == "💳 Pagos":
    st.title("💳 Pagos Mercado Pago")

    tab1, tab2 = st.tabs(["Pendientes", "Todos los pagos"])

    with tab1:
        st.subheader("Pagos pendientes de aprobación")
        pagos, err = api_get('/api/admin/pagos', {'estado': 'pendiente'})
        if err:
            st.error(err)
        elif not pagos:
            st.success("No hay pagos pendientes.")
        else:
            for r in pagos:
                with st.expander(f"Pago #{r['id']} — {r.get('nombre') or r['usuario_dni']} — ${r['monto']} — {r['paquete']}"):
                    st.write(f"**DNI:** {r['usuario_dni']}")
                    st.write(f"**Fichas:** {r['fichas']} | **Monto:** ${r['monto']}")
                    st.write(f"**Pasarela:** {r['pasarela']}")
                    st.write(f"**External ID:** `{r.get('external_id')}`")
                    st.write(f"**Fecha:** {r['fecha_creacion']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Aprobar #{r['id']}", key=f"ap_{r['id']}"):
                            _, err = api_post(f"/api/admin/pago/{r['id']}/aprobar")
                            if err:
                                st.error(err)
                            else:
                                st.success(f"Pago #{r['id']} aprobado.")
                                st.rerun()
                    with col_b:
                        if st.button(f"❌ Rechazar #{r['id']}", key=f"re_{r['id']}"):
                            _, err = api_post(f"/api/admin/pago/{r['id']}/rechazar")
                            if err:
                                st.error(err)
                            else:
                                st.warning(f"Pago #{r['id']} rechazado.")
                                st.rerun()

    with tab2:
        st.subheader("Historial completo de pagos")
        estado_fil = st.selectbox("Filtrar por estado", ["todos", "pendiente", "aprobado", "rechazado", "cancelado"])
        pagos, err = api_get('/api/admin/pagos', {'estado': estado_fil})
        if err:
            st.error(err)
        elif pagos:
            import pandas as pd
            df = pd.DataFrame(pagos)
            cols = [c for c in ['id','usuario_dni','nombre','paquete','fichas','monto','pasarela','estado','fecha_creacion'] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Sin registros.")
