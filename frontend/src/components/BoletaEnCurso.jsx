// BoletaEnCurso.jsx
// Muestra la boleta jugada mientras la fecha está en curso.
// - Fibrón verde  → partido finalizado y acertado
// - Fibrón naranja → partido finalizado y errado
// - Sin color     → partido pendiente
// - Mini panel de % aciertos/desaciertos en tiempo real

import { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/fetchWithAuth';

const MESES_ES = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC'];

function formatFecha(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return `${String(d.getDate()).padStart(2,'0')} ${MESES_ES[d.getMonth()]} ${d.getFullYear()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

function FilaPartido({ p, idx }) {
    let claseRow = 'bec-fila';
    let claseLabel = '';
    let indicador = null;

    if (p.acierto === true) {
        claseRow += ' bec-fila--acierto';
        claseLabel = 'bec-fibron bec-fibron--verde';
        indicador = <span className="bec-indicador bec-indicador--ok">✓</span>;
    } else if (p.acierto === false) {
        claseRow += ' bec-fila--error';
        claseLabel = 'bec-fibron bec-fibron--naranja';
        indicador = <span className="bec-indicador bec-indicador--err">✗</span>;
    }

    const marcador = p.resultado
        ? <span className="bec-marcador">{p.goles_local ?? '-'}&nbsp;-&nbsp;{p.goles_visitante ?? '-'}</span>
        : <span className="bec-hora">{p.fecha_hora ? new Date(p.fecha_hora).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}) : '--:--'}</span>;

    return (
        <div className={claseRow}>
            {/* Número */}
            <span className="bec-num">{idx + 1}.</span>

            {/* Local */}
            <span className={`bec-equipo bec-equipo--local${claseLabel ? ' ' + claseLabel : ''}`}>
                {p.local}
            </span>

            {/* VS / marcador / hora */}
            <span className="bec-centro">
                {p.resultado
                    ? marcador
                    : <span className="bec-vs-sep">vs</span>
                }
            </span>

            {/* Visitante */}
            <span className={`bec-equipo bec-equipo--visita${claseLabel ? ' ' + claseLabel : ''}`}>
                {p.visitante}
            </span>

            {/* Apuesta */}
            <span className="bec-sel bec-sel--badge">{p.seleccion || '—'}</span>

            {/* Indicador */}
            <span className="bec-ind-col">{indicador}</span>
        </div>
    );
}

function MiniPanelStats({ jugada }) {
    const { finalizados, total, aciertos_parciales, errores_parciales, pct_aciertos, pct_errores } = jugada;
    if (finalizados === 0) return null;

    return (
        <div className="bec-stats">
            <div className="bec-stats-titulo">⚡ RESULTADOS EN VIVO</div>
            <div className="bec-stats-fila">
                <span className="bec-stats-label">PARTIDOS JUGADOS</span>
                <span className="bec-stats-val">{finalizados}/{total}</span>
            </div>
            <div className="bec-stats-barras">
                <div className="bec-barra-wrap">
                    <div className="bec-barra-label bec-barra-label--ok">ACIERTOS</div>
                    <div className="bec-barra-track">
                        <div
                            className="bec-barra-fill bec-barra-fill--ok"
                            style={{ width: `${pct_aciertos}%` }}
                        />
                    </div>
                    <span className="bec-barra-pct">{aciertos_parciales} ({pct_aciertos}%)</span>
                </div>
                <div className="bec-barra-wrap">
                    <div className="bec-barra-label bec-barra-label--err">DESACIERTOS</div>
                    <div className="bec-barra-track">
                        <div
                            className="bec-barra-fill bec-barra-fill--err"
                            style={{ width: `${pct_errores}%` }}
                        />
                    </div>
                    <span className="bec-barra-pct">{errores_parciales} ({pct_errores}%)</span>
                </div>
            </div>
        </div>
    );
}

export default function BoletaEnCurso({ jugada: jugadaInicial, nroFecha }) {
    const [jugada, setJugada] = useState(jugadaInicial);

    // Auto-refresco cada 60s mientras la fecha está en curso
    useEffect(() => {
        setJugada(jugadaInicial);
    }, [jugadaInicial]);

    useEffect(() => {
        const t = setInterval(async () => {
            try {
                const resp = await fetchWithAuth('/api/mi-jugada-activa');
                const data = await resp.json();
                if (resp.ok && data.jugada) setJugada(data.jugada);
            } catch { /* ignorar errores transitorios */ }
        }, 60_000);
        return () => clearInterval(t);
    }, []);

    if (!jugada) return null;

    const fechaCierre = formatFecha(jugada.fecha_registro);
    const fechaCerrada = jugada.aciertos_totales !== null;

    return (
        <section className="bec-panel card-retro">
            <div className="bec-header">
                <h1 className="logo-sabes">SABES DE FUTBOL</h1>
                <div className="bec-fecha-badge">
                    FECHA Nº <span className="num-rojo">{String(nroFecha).padStart(5,'0')}</span>
                </div>
            </div>

            <div className="bec-subtitulo">
                {fechaCerrada
                    ? <span className="bec-estado bec-estado--cerrada">✓ FECHA CERRADA — {jugada.aciertos_totales} ACIERTOS</span>
                    : <span className="bec-estado bec-estado--vivo bec-blink-txt">● EN CURSO</span>
                }
                <span className="bec-jugado-el">Jugado el {fechaCierre}</span>
            </div>

            <div className="bec-grid">
                <div className="bec-header-row">
                    <span className="bec-col-num">#</span>
                    <span className="bec-col-local">LOCAL</span>
                    <span className="bec-col-centro">RESULT.</span>
                    <span className="bec-col-visita">VISITANTE</span>
                    <span className="bec-col-sel">APUESTA</span>
                    <span className="bec-col-ind" />
                </div>
                {jugada.partidos.map((p, i) => (
                    <FilaPartido key={i} p={p} idx={i} />
                ))}
            </div>

            {!fechaCerrada && <MiniPanelStats jugada={jugada} />}

            {fechaCerrada && (
                <div className="bec-resumen-final">
                    <span className="bec-resumen-txt">
                        RESULTADO FINAL: <strong>{jugada.aciertos_totales}</strong> DE <strong>{jugada.total}</strong> ACIERTOS
                    </span>
                </div>
            )}
        </section>
    );
}
