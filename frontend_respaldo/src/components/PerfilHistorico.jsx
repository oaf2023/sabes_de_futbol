import React from 'react';

export default function PerfilHistorico() {
    return (
        <section className="card" style={{
            backgroundColor: 'var(--color-secundario)',
            border: '2px solid #ccc',
            display: 'flex',
            gap: '15px',
            alignItems: 'center'
        }}>
            <div style={{
                width: '80px',
                height: '100px',
                backgroundColor: '#d2b48c',
                border: '3px solid #fff',
                boxShadow: '2px 2px 5px rgba(0,0,0,0.2)',
                backgroundImage: 'radial-gradient(circle at 50% 30%, #5c3c1e 15px, transparent 16px), radial-gradient(ellipse at 50% 100%, #5c3c1e 35px, transparent 36px)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div style={{
                    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(139, 69, 19, 0.2)', mixBlendMode: 'multiply'
                }}></div>
            </div>

            <div>
                <h2 style={{
                    fontFamily: 'var(--font-titulo)', color: 'var(--color-primario)',
                    fontSize: '1.2rem', marginBottom: '5px', borderBottom: '1px solid var(--color-primario)'
                }}>MURAL DE LEYENDAS</h2>

                <p style={{ fontSize: '0.85rem', lineHeight: '1.4' }}>
                    Héroe: <span style={{ fontFamily: 'var(--font-titulo)', fontWeight: 'bold' }}>Ramón Negrete Mercedes</span>
                </p>
                <p style={{ fontSize: '0.85rem', lineHeight: '1.4' }}>
                    Hito: <span style={{ fontFamily: 'var(--font-titulo)', fontWeight: 'bold' }}>1er Ganador (1972)</span>
                </p>
                <p style={{ fontSize: '0.85rem', lineHeight: '1.4', marginTop: '5px', color: '#555', fontStyle: 'italic' }}>
                    <small>✨ Easter Egg: Primer partido histórico fue Estudiantes LP vs Atlanta (2-0) el 27/02/1972.</small>
                </p>
            </div>
        </section>
    );
}
