import React, { useState, useEffect } from 'react';

export default function Boleta({ partidos, nroFecha, usuarioDni, fichas = 0, pendientes = 0, onJugar, onAgregarAlCarrito, onAbrirCompra }) {
    const [boletaUsuario, setBoletaUsuario] = useState([]);
    const [loading, setLoading] = useState(false);
    const opciones = ['L', 'E', 'V'];

    useEffect(() => {
        if (partidos.length > 0) {
            setBoletaUsuario(new Array(partidos.length).fill(null));
        }
    }, [partidos]);

    const setApuesta = (idx, valor) => {
        const nueva = [...boletaUsuario];
        nueva[idx] = valor;
        setBoletaUsuario(nueva);
    };

    const handleOtraJugada = () => {
        const vacias = boletaUsuario.filter(s => !s).length;
        if (vacias > 0) {
            alert(`Completá todos los partidos para acumular otra jugada. Faltan ${vacias}.`);
            return;
        }
        onAgregarAlCarrito([...boletaUsuario]);
        setBoletaUsuario(new Array(partidos.length).fill(null));
        alert("✅ Jugada agregada al carrito. ¡Podés hacer otra!");
    };

    const handleConfirmarBoleta = async () => {
        const vacias = boletaUsuario.filter(s => !s).length;
        if (vacias > 0) {
            alert(`❌ Boleta incompleta. Completá los ${vacias} partidos restantes de la boleta actual.`);
            return;
        }
        setLoading(true);
        onJugar([...boletaUsuario]);
        setBoletaUsuario(new Array(partidos.length).fill(null));
        setLoading(false);
    };

    return (
        <section className="boleta-digital card-retro">
            <div className="boleta-header">
                <h1 className="logo-sabes">SABES DE FUTBOL</h1>
                <div className="boleta-numero">
                    FECHA Nº <span className="num-rojo" id="nro-fecha">{String(nroFecha).padStart(5, '0')}</span>
                </div>
            </div>

            <div className="boleta-grid">
                <div className="row header-row">
                    <span className="partido">PARTIDO</span>
                    <span className="opcion">L</span>
                    <span className="opcion">E</span>
                    <span className="opcion">V</span>
                </div>

                <div id="filas-boleta">
                    {partidos.map((partido, idx) => (
                        <div key={idx} className="row">
                            <span className="partido">
                                <strong>{idx + 1}.</strong> {partido.nombre}
                            </span>
                            {opciones.map(opt => (
                                <span key={opt} className="opcion">
                                    <input
                                        className="input-radio"
                                        type="radio"
                                        name={`partido_${idx}`}
                                        value={opt}
                                        checked={boletaUsuario[idx] === opt}
                                        onChange={() => setApuesta(idx, opt)}
                                    />
                                </span>
                            ))}
                        </div>
                    ))}
                    {partidos.length === 0 && <p className="no-partidos">Cargando partidos...</p>}
                </div>
            </div>

            <div id="status-jugadas" className="status-panel">
                <div className="status-info">
                    <p>Fichas: <span className="dato" id="user-fichas">{fichas}</span></p>
                    <p>Pendientes: <span className="dato" id="pendientes-count">{pendientes}</span></p>
                </div>
                <button
                    id="btn-comprar-fichas"
                    className="btn-retro-sm"
                    onClick={onAbrirCompra}
                >
                    COMPRAR FICHAS
                </button>
            </div>

            <div className="botones-juego">
                <button
                    id="btn-otra-jugada"
                    className="btn-jugar"
                    onClick={handleOtraJugada}
                    disabled={loading || partidos.length === 0}
                >
                    OTRA JUGADA
                </button>
                <button
                    id="btn-confirmar-boleta"
                    className="btn-jugar"
                    onClick={handleConfirmarBoleta}
                    disabled={loading || partidos.length === 0}
                >
                    {loading ? 'PROCESANDO...' : 'JUEGA BOLETA'}
                </button>
            </div>
        </section>
    );
}
