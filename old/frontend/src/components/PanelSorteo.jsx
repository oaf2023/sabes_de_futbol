import React from 'react';

export default function PanelSorteo({ partidos, estadoSorteo }) {
    // Encontrar el último partido sorteado o mostrar TBD
    const idxSorteado = partidos.findLastIndex(p => p.resultado_final !== null);
    const partidoActual = idxSorteado >= 0 ? partidos[idxSorteado] : null;

    return (
        <section className="card-pizarron card">
            <h2 className="titulo-retro" style={{ textAlign: 'center', color: '#f1c40f', marginBottom: '20px' }}>RESULTADOS EN VIVO</h2>

            <div style={{
                height: '120px', background: '#111', border: '4px solid #444',
                borderRadius: '8px', marginBottom: '20px', display: 'flex',
                justifyContent: 'center', alignItems: 'center', overflow: 'hidden',
                position: 'relative', boxShadow: 'inset 0 0 15px rgba(0,0,0,0.8)'
            }}>
                {estadoSorteo === 'ESPERANDO' && (
                    <div className="numero-digital" style={{ fontSize: '4rem', color: '#555' }}>ESPERANDO</div>
                )}
                {estadoSorteo === 'SORTEANDO' && partidoActual && (
                    <div style={{ textAlign: 'center' }}>
                        <div style={{ color: '#aaa', fontSize: '0.9rem', marginBottom: '5px' }}>{partidoActual.nombre}</div>
                        <div className="numero-digital" style={{ fontSize: '5rem', color: 'var(--color-acento)', textShadow: '0 0 10px var(--color-acento)' }}>
                            {partidoActual.resultado_final}
                        </div>
                    </div>
                )}
                {estadoSorteo === 'SORTEANDO' && !partidoActual && (
                    <div className="numero-digital" style={{ fontSize: '4rem', color: 'var(--color-acento)', textShadow: '0 0 10px var(--color-acento)' }}>...</div>
                )}
                {estadoSorteo === 'FINALIZADO' && (
                    <div className="numero-digital" style={{ fontSize: '4rem', color: 'var(--color-acento)', textShadow: '0 0 10px var(--color-acento)' }}>FINALIZADO</div>
                )}
            </div>

            {/* Ticker de resultados estilo crónica/marcador antiguo */}
            <div style={{
                background: '#000', color: '#0f0', padding: '10px',
                overflow: 'hidden', whiteSpace: 'nowrap', borderRadius: '4px',
                fontSize: '1.2rem', display: 'flex'
            }}>
                <div className="numero-digital" style={{ animation: 'ticker 15s linear infinite', paddingLeft: '100%' }}>
                    {partidos.map(p => {
                        if (p.resultado_final) return `${p.nombre} [${p.resultado_final}] | `;
                        return `${p.nombre} [?] | `;
                    })}
                </div>
            </div>

            <style>{`
        @keyframes ticker {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-100%, 0); }
        }
      `}</style>
        </section>
    );
}
