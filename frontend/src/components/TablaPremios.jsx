import React, { useEffect, useState } from 'react';

export default function TablaPremios({ estadoSorteo, aciertos }) {
    const [claseGlow, setClaseGlow] = useState('');

    useEffect(() => {
        if (estadoSorteo === 'FINALIZADO' && aciertos === 13) {
            setClaseGlow('glow');
        } else {
            setClaseGlow('');
        }
    }, [estadoSorteo, aciertos]);

    return (
        <section className="card-madera card">
            <h2 style={{ fontFamily: 'var(--font-titulo)', textTransform: 'uppercase', marginBottom: '15px', textShadow: '2px 2px 2px rgba(0,0,0,0.5)' }}>POZO ACUMULADO</h2>

            <div className={claseGlow} style={{
                background: '#000', padding: '15px', borderRadius: '5px',
                border: '2px solid gold', marginBottom: '30px'
            }}>
                <span style={{ fontFamily: 'var(--font-numeros)', fontSize: '3rem', color: 'gold', textShadow: '0 0 10px gold' }}>$ 1.000.000</span>
            </div>

            {estadoSorteo === 'FINALIZADO' && (
                <div style={{ marginBottom: '20px', padding: '10px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px' }}>
                    <div style={{ fontFamily: 'var(--font-titulo)', fontSize: '1.2rem' }}>Aciertos: {aciertos}</div>
                    {aciertos === 13 && <div style={{ color: 'gold', fontWeight: 'bold' }}>¡PREMIO MAYOR! FELICITACIONES</div>}
                    {aciertos >= 10 && aciertos < 13 && <div style={{ color: 'lime' }}>¡GANASTE UN PREMIO MENOR!</div>}
                    {aciertos < 10 && <div style={{ color: '#ff9999' }}>MALA SUERTE, SEGUI PARTICIPANDO</div>}
                </div>
            )}

            <ul style={{ listStyle: 'none', textAlign: 'left' }}>
                <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px dashed rgba(255,255,255,0.3)', fontFamily: 'var(--font-titulo)', fontSize: '1.1rem', textShadow: '1px 1px 1px rgba(0,0,0,0.5)' }}>
                    <span>13 Aciertos</span>
                    <span style={{ color: 'gold', fontWeight: 'bold' }}>$1.000.000</span>
                </li>
                <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px dashed rgba(255,255,255,0.3)', fontFamily: 'var(--font-titulo)', fontSize: '1.1rem', textShadow: '1px 1px 1px rgba(0,0,0,0.5)' }}>
                    <span>12 Aciertos</span>
                    <span>$50.000</span>
                </li>
                <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px dashed rgba(255,255,255,0.3)', fontFamily: 'var(--font-titulo)', fontSize: '1.1rem', textShadow: '1px 1px 1px rgba(0,0,0,0.5)' }}>
                    <span>11 Aciertos</span>
                    <span>Recupero x10</span>
                </li>
                <li style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', borderBottom: '1px dashed rgba(255,255,255,0.3)', fontFamily: 'var(--font-titulo)', fontSize: '1.1rem', textShadow: '1px 1px 1px rgba(0,0,0,0.5)' }}>
                    <span>10 Aciertos</span>
                    <span>Recupero x2</span>
                </li>
            </ul>

            <style>{`
        .glow { animation: pulseGlow 2s infinite; }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 5px gold; }
            50% { box-shadow: 0 0 20px gold; }
            100% { box-shadow: 0 0 5px gold; }
        }
      `}</style>
        </section>
    );
}
