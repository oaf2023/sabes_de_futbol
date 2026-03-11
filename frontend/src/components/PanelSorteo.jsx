import React from 'react';

export default function PanelSorteo({ partidos, estadoSorteo, loading }) {
    const idxSorteado = partidos.findLastIndex(p => p.resultado_final !== null);
    const partidoActual = idxSorteado >= 0 ? partidos[idxSorteado] : null;

    return (
        <section className="panel-sorteo card-pizarron">
            <h2 className="titulo-pizarron">RESULTADOS EN VIVO</h2>
            <div className="fecha-panel-contenedor">
                <span className="fecha-pizarron">
                    {estadoSorteo === 'ESPERANDO' ? 'ESPERANDO JUGADA' : 'SORTEO EN CURSO'}
                </span>
            </div>

            <div className="ruleta-container">
                <div className="ruleta-slot" id="slot-1">
                    {estadoSorteo === 'ESPERANDO' ? '?' : (partidoActual ? partidoActual.resultado_final : '...')}
                </div>
            </div>

            <div className="ticker-resultados">
                <div className="ticker-text">
                    {partidos.map((p, i) => (
                        <span key={i}>
                            {p.nombre} {p.resultado_final ? `[${p.resultado_final}]` : ''} {i < partidos.length - 1 ? ' | ' : ''}
                        </span>
                    ))}
                    {partidos.length === 0 && "NO HAY PARTIDOS ACTIVOS | "}
                </div>
            </div>
        </section>
    );
}
