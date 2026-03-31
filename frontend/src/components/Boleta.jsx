import React, { useState, useEffect } from 'react';

export default function Boleta({
    partidos,
    nroFecha,
    usuarioDni,
    numeroDeSocio, // Nueva prop
    fichas = 0,
    pendientes = 0,
    fechaComenzada = false,   // true = la fecha ya arrancó, no se puede jugar
    yaJugo = false,           // true = ya tiene jugada guardada en esta fecha
    onJugar,
    onAgregarAlCarrito,
    onAbrirCompra
}) {
    const [boletaUsuario, setBoletaUsuario] = useState([]);
    const [loading, setLoading] = useState(false);
    const opciones = ['L', 'E', 'V'];

    useEffect(() => {
        if (partidos.length > 0) {
            setBoletaUsuario(new Array(partidos.length).fill(null));
        }
    }, [partidos]);

    // Boleta completa: ningún partido sin selección
    const todosSeleccionados = partidos.length > 0 && boletaUsuario.every(s => s !== null);

    // Bloqueo global: si la fecha comenzó o el usuario ya jugó
    const bloqueada = fechaComenzada || yaJugo;

    const setApuesta = (idx, valor) => {
        if (bloqueada) return;
        const nueva = [...boletaUsuario];
        nueva[idx] = valor;
        setBoletaUsuario(nueva);
    };

    const handleOtraJugada = () => {
        if (bloqueada) return;
        const vacias = boletaUsuario.filter(s => !s).length;
        if (vacias > 0) {
            alert(`Completá todos los partidos para acumular otra jugada. Faltan ${vacias}.`);
            return;
        }
        onAgregarAlCarrito([...boletaUsuario]);
        setBoletaUsuario(new Array(partidos.length).fill(null));
    };

    const handleConfirmarBoleta = async () => {
        if (bloqueada) return;
        if (!todosSeleccionados) {
            alert("⚠️ Debes marcar todos los resultados antes de jugar.");
            return;
        }
        setLoading(true);
        onJugar([...boletaUsuario]);
        setBoletaUsuario(new Array(partidos.length).fill(null));
        setLoading(false);
    };

    // Mensaje de estado de la boleta
    let mensajeEstado = null;
    if (yaJugo) {
        mensajeEstado = { texto: '✓ BOLETA YA JUGADA', clase: 'boleta-estado boleta-estado--jugada' };
    } else if (fechaComenzada) {
        mensajeEstado = { texto: '⚠ FECHA EN CURSO — CIERRE VENCIDO', clase: 'boleta-estado boleta-estado--cerrada' };
    }

    return (
        <section className={`boleta-digital card-retro${bloqueada ? ' boleta-bloqueada' : ''}`}>
            <div className="boleta-header">
                <h1 className="logo-sabes">SABES DE FUTBOL</h1>
                <div className="boleta-numero">
                    FECHA Nº <span className="num-rojo" id="nro-fecha">{String(nroFecha).padStart(5, '0')}</span>
                </div>
            </div>

            {mensajeEstado && (
                <div className={mensajeEstado.clase}>{mensajeEstado.texto}</div>
            )}

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
                                        disabled={bloqueada}
                                    />
                                </span>
                            ))}
                        </div>
                    ))}
                    {partidos.length === 0 && <p className="no-partidos">Cargando partidos...</p>}
                </div>
            </div>

            <div id="status-jugadas" className="status-panel-minimal">
                <div className="status-info-row">
                    <p>Socio: <span className="dato">{numeroDeSocio}</span></p>
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
                    disabled={loading || partidos.length === 0 || bloqueada || !todosSeleccionados}
                    title={!todosSeleccionados ? 'Marcá todos los partidos primero' : ''}
                >
                    OTRA JUGADA
                </button>
                <button
                    id="btn-confirmar-boleta"
                    className={`btn-jugar${todosSeleccionados && !bloqueada ? ' btn-jugar--listo' : ''}`}
                    onClick={handleConfirmarBoleta}
                    disabled={loading || partidos.length === 0 || bloqueada}
                >
                    {loading ? 'PROCESANDO...' : 'JUEGA BOLETA'}
                </button>
            </div>
        </section>
    );
}
