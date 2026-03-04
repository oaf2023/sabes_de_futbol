import React from 'react';

export default function Boleta({ partidos, boletaUsuario, setApuesta, handleJugar, estadoSorteo }) {
    // L, X, V options instead of L, E, V per prompt instructions
    const opciones = ['L', 'X', 'V'];

    return (
        <section className="boleta-digital card">
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '2px dashed #ccc',
                paddingBottom: '10px',
                marginBottom: '15px'
            }}>
                <h1 className="logo-sabes" style={{ fontFamily: 'var(--font-titulo)', color: 'var(--color-primario)', fontSize: '2.5rem', letterSpacing: '2px', textShadow: '2px 2px 0px rgba(0,0,0,0.1)' }}>SABES DE FUTBOL</h1>
                <div style={{ fontFamily: 'var(--font-numeros)', fontSize: '1.5rem' }}>
                    Nº <span style={{ color: 'var(--color-error)', fontSize: '1.8rem' }}>007842</span>
                </div>
            </div>

            <div style={{
                position: 'absolute', top: '30%', left: '10%', transform: 'rotate(-30deg)',
                fontFamily: 'var(--font-titulo)', fontSize: '2rem', color: 'rgba(26, 82, 118, 0.1)',
                pointerEvents: 'none', zIndex: 0, border: '3px double rgba(26, 82, 118, 0.1)',
                padding: '5px', textAlign: 'center'
            }}>LOTERÍA NACIONAL</div>

            <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '5px 0', borderBottom: '2px solid var(--color-primario)', marginBottom: '5px', fontWeight: 'bold', color: 'var(--color-primario)', fontFamily: 'var(--font-titulo)' }}>
                    <span>PARTIDO</span>
                    <span style={{ textAlign: 'center' }}>L</span>
                    <span style={{ textAlign: 'center' }}>X</span>
                    <span style={{ textAlign: 'center' }}>V</span>
                </div>

                {partidos.map((partido, idx) => (
                    <div key={partido.id} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', padding: '5px 0', borderBottom: '1px solid #eee', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.85rem' }}>
                            <strong>{idx + 1}.</strong> {partido.nombre}
                        </span>
                        {opciones.map(opt => {
                            // Highlight si acertó
                            const esAcierto = estadoSorteo === 'FINALIZADO' && boletaUsuario[idx] === opt && partido.resultado_final === opt;
                            const fallo = estadoSorteo === 'FINALIZADO' && boletaUsuario[idx] === opt && partido.resultado_final !== opt;

                            const bgColor = esAcierto ? 'var(--color-acento)' : (fallo ? 'var(--color-error)' : 'transparent');
                            const color = esAcierto || fallo ? 'white' : 'inherit';

                            return (
                                <span key={opt} style={{ textAlign: 'center', backgroundColor: bgColor, color, borderRadius: '4px' }}>
                                    <input
                                        type="radio"
                                        name={`partido_${idx}`}
                                        value={opt}
                                        checked={boletaUsuario[idx] === opt}
                                        onChange={() => setApuesta(idx, opt)}
                                        disabled={estadoSorteo !== 'ESPERANDO'}
                                        style={{ accentColor: 'var(--color-primario)', width: '18px', height: '18px', cursor: 'pointer', margin: '4px' }}
                                    />
                                </span>
                            )
                        })}
                    </div>
                ))}
            </div>

            <button
                onClick={handleJugar}
                disabled={estadoSorteo !== 'ESPERANDO'}
                style={{
                    width: '100%', marginTop: '20px', padding: '15px', backgroundColor: 'var(--color-acento)',
                    color: 'var(--color-blanco)', border: 'none', fontFamily: 'var(--font-titulo)',
                    fontSize: '1.2rem', cursor: estadoSorteo === 'ESPERANDO' ? 'pointer' : 'not-allowed',
                    boxShadow: '4px 4px 0px rgba(0,0,0,0.2)', transition: 'all 0.1s'
                }}
            >
                {estadoSorteo === 'ESPERANDO' ? 'JUGAR FICHAS' : 'SORTEO EN CURSO...'}
            </button>
        </section>
    );
}
