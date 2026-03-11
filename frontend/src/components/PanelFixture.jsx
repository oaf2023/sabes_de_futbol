// PanelFixture.jsx
// Panel lateral retro de fixture — estilo pizarrón AFA profesional
// Agrupa por día, muestra marcadores en finalizados, hora + estado en pendientes.
// Auto-refresca cada 60s.

import React, { useState, useEffect } from 'react';

const DIAS_ES = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB'];
const MESES_ES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];

function parseFechaHora(iso) {
    if (!iso) return null;
    const d = new Date(iso);
    return isNaN(d.getTime()) ? null : d;
}

function claveDia(d) {
    if (!d) return '---';
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    return `${DIAS_ES[d.getDay()]} ${dd}/${mm}`;
}

function horaStr(d) {
    if (!d) return '--:--';
    return d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function agruparPorDia(partidos) {
    const grupos = [];
    const mapa = {};
    partidos.forEach(p => {
        const d = parseFechaHora(p.fecha_hora);
        const clave = claveDia(d);
        if (!mapa[clave]) {
            mapa[clave] = [];
            grupos.push({ clave, items: mapa[clave] });
        }
        mapa[clave].push({ ...p, _fecha: d });
    });
    return grupos;
}

function estadoPartido(p) {
    if (p.resultado !== null && p.resultado !== undefined) return 'fin';
    // Comparamos con hora actual para "en juego" (+-110min de fecha_hora)
    if (p._fecha) {
        const ahora = Date.now();
        const inicio = p._fecha.getTime();
        const diff = ahora - inicio;
        if (diff >= 0 && diff < 110 * 60 * 1000) return 'live';
    }
    return 'pend';
}

function MarcadorFin({ p }) {
    const gl = p.goles_local ?? '-';
    const gv = p.goles_visitante ?? '-';
    const res = p.resultado; // 'L', 'E', 'V'
    return (
        <div className="fx2-marcador fx2-marcador--fin">
            <span className={`fx2-gol ${res === 'L' ? 'fx2-gol--bold' : ''}`}>{gl}</span>
            <span className="fx2-vsep">-</span>
            <span className={`fx2-gol ${res === 'V' ? 'fx2-gol--bold' : ''}`}>{gv}</span>
        </div>
    );
}

function MarcadorLive({ p }) {
    const gl = p.goles_local ?? '-';
    const gv = p.goles_visitante ?? '-';
    return (
        <div className="fx2-marcador fx2-marcador--live">
            <span className="fx2-live-dot" />
            <span className="fx2-gol-live">{gl}</span>
            <span className="fx2-vsep-live">-</span>
            <span className="fx2-gol-live">{gv}</span>
        </div>
    );
}

function MarcadorPend({ p }) {
    return (
        <div className="fx2-marcador fx2-marcador--pend">
            <span className="fx2-hora">{horaStr(p._fecha)}</span>
        </div>
    );
}

function FilaPartido({ p }) {
    const estado = estadoPartido(p);

    const marcador = estado === 'fin'
        ? <MarcadorFin p={p} />
        : estado === 'live'
            ? <MarcadorLive p={p} />
            : <MarcadorPend p={p} />;

    return (
        <div className={`fx2-fila fx2-fila--${estado}`}>
            {/* indicador lateral de estado */}
            <div className={`fx2-estado-dot fx2-dot--${estado}`} title={
                estado === 'fin' ? 'Finalizado' : estado === 'live' ? 'En juego' : 'Pendiente'
            } />

            <span className="fx2-equipo fx2-equipo--local" title={p.local}>
                {p.local}
            </span>

            {marcador}

            <span className="fx2-equipo fx2-equipo--visita" title={p.visitante}>
                {p.visitante}
            </span>
        </div>
    );
}

function CabeceraDia({ clave }) {
    return (
        <div className="fx2-dia-header">
            <span className="fx2-dia-linea" />
            <span className="fx2-dia-label">{clave}</span>
            <span className="fx2-dia-linea" />
        </div>
    );
}

export default function PanelFixture({ nroFecha }) {
    const [partidos, setPartidos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const [ultimaAct, setUltimaAct] = useState(null);

    const cargar = async () => {
        try {
            setError(false);
            const resp = await fetch('/api/partidos');
            if (!resp.ok) throw new Error('API error');
            const data = await resp.json();
            setPartidos(data.partidos || []);
        } catch {
            setError(true);
        } finally {
            setLoading(false);
            setUltimaAct(new Date());
        }
    };

    useEffect(() => {
        cargar();
        const t = setInterval(cargar, 60_000);
        return () => clearInterval(t);
    }, [nroFecha]);

    const finalizados = partidos.filter(p => p.resultado !== null && p.resultado !== undefined).length;
    const total = partidos.length;
    const porcentaje = total > 0 ? Math.round((finalizados / total) * 100) : 0;
    const grupos = agruparPorDia(partidos);

    return (
        <aside className="fx2-panel">

            {/* ── CABECERA ── */}
            <div className="fx2-header">
                <div className="fx2-header-top">
                    <div className="fx2-escudo-afa">
                        <span className="fx2-afa-icon">⚽</span>
                    </div>
                    <div className="fx2-header-info">
                        <span className="fx2-titulo">PRIMERA DIVISIÓN</span>
                        <span className="fx2-subtitulo">TORNEO APERTURA 2026</span>
                    </div>
                    <div className="fx2-fecha-badge">
                        <span className="fx2-fecha-lbl">FEC</span>
                        <span className="fx2-fecha-num">{String(nroFecha || 0).padStart(2, '0')}</span>
                    </div>
                </div>

                {/* Barra de progreso */}
                {total > 0 && (
                    <div className="fx2-progreso">
                        <div className="fx2-progreso-bar">
                            <div className="fx2-progreso-fill" style={{ width: `${porcentaje}%` }} />
                        </div>
                        <span className="fx2-progreso-txt">
                            {finalizados}/{total} <span className="fx2-progreso-sub">JUGADOS</span>
                        </span>
                    </div>
                )}
            </div>

            {/* ── LEYENDA ── */}
            <div className="fx2-leyenda">
                <span className="fx2-ley-item"><span className="fx2-ley-dot fx2-dot--fin" />FIN</span>
                <span className="fx2-ley-item"><span className="fx2-ley-dot fx2-dot--live fx2-blink" />EN JUEGO</span>
                <span className="fx2-ley-item"><span className="fx2-ley-dot fx2-dot--pend" />PEND</span>
            </div>

            {/* ── CUERPO ── */}
            <div className="fx2-body">
                {loading && (
                    <div className="fx2-estado-msg">
                        <span className="fx2-blink">▋</span> CARGANDO DATOS…
                    </div>
                )}
                {!loading && error && (
                    <div className="fx2-estado-msg fx2-estado-msg--err">
                        ✕ SIN CONEXIÓN
                    </div>
                )}
                {!loading && !error && total === 0 && (
                    <div className="fx2-estado-msg">
                        SIN PARTIDOS ACTIVOS
                    </div>
                )}

                {grupos.map(({ clave, items }) => (
                    <div key={clave} className="fx2-grupo">
                        <CabeceraDia clave={clave} />
                        {items.map((p, i) => <FilaPartido key={i} p={p} />)}
                    </div>
                ))}
            </div>

            {/* ── PIE ── */}
            <div className="fx2-pie">
                <span className="fx2-pie-txt">
                    {ultimaAct
                        ? `ACT. ${ultimaAct.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })}`
                        : 'ACTUALIZANDO…'
                    }
                </span>
                <span className="fx2-pie-sep">•</span>
                <span className="fx2-pie-txt">AUTO 60s</span>
            </div>
        </aside>
    );
}
