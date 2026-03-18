import React from 'react';

export default function TablaPremios({ estadoSorteo, aciertos }) {
    return (
        <section className="tabla-premios card-madera">
            <h2>POZO ACUMULADO</h2>
            <div className={`premio-mayor ${estadoSorteo === 'FINALIZADO' && aciertos === 13 ? 'glow' : ''}`}>
                <span className="amount">1.000.000</span>
                <span className="currency" style={{ fontSize: '0.6em', marginLeft: '5px' }}>fichas</span>
            </div>

            <ul className="lista-premios">
                <li className="premio-item">
                    <span>Total de Aciertos</span>
                    <span className="dorado">1.000.000 <small>fichas</small></span>
                </li>
                <li className="premio-item">
                    <span>Total de Aciertos - 1</span>
                    <span>50.000 <small>fichas</small></span>
                </li>
                <li className="premio-item">
                    <span>Total de Aciertos - 2</span>
                    <span>Recupero x10 <small>fichas</small></span>
                </li>
                <li className="premio-item">
                    <span>Total de Aciertos - 3</span>
                    <span>Recupero x2 <small>fichas</small></span>
                </li>
            </ul>

            {estadoSorteo === 'FINALIZADO' && (
                <div style={{ marginTop: '20px', padding: '10px', background: 'rgba(0,0,0,0.2)', borderRadius: '4px' }}>
                    <p style={{ fontFamily: 'var(--font-titulo)', fontSize: '0.9rem' }}>Aciertos: {aciertos}</p>
                </div>
            )}
        </section>
    );
}
