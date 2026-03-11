import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../utils/fetchWithAuth';

export default function PerfilHistorico({ usuario, onVerTicket }) {
    const [historial, setHistorial] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (usuario?.dni) {
            fetchHistorial(usuario.dni);
        }
    }, [usuario]);

    const fetchHistorial = async (dni) => {
        try {
            const resp = await fetchWithAuth(`/api/historial/${dni}`);
            const data = await resp.json();
            if (resp.ok) setHistorial(data);
        } catch (err) {
            console.error("Error al cargar historial:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="historial-tickets card-madera" style={{ marginTop: '20px' }}>
            <h2 className="titulo-pizarron">MIS JUGADAS</h2>
            <div className="historial-container-inline" id="historial-ticket-style">
                {loading ? (
                    <p className="no-jugadas">Cargando jugadas...</p>
                ) : historial.length === 0 ? (
                    <p className="no-jugadas">Aún no tenés jugadas. ¡Empezá hoy!</p>
                ) : (
                    historial.sort((a, b) => b.id - a.id).map((ticket) => (
                        <div
                            key={ticket.id}
                            className="ticket-historial card-retro"
                            onClick={() => onVerTicket(ticket.id)}
                            style={{ cursor: 'pointer' }}
                        >
                            <div className="ticket-header-sm">
                                <span>FECHA #{ticket.nro_fecha || '00000'}</span>
                                <span className="fecha-sm">{ticket.fecha || ''}</span>
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--color-acento)', marginBottom: '5px' }}>
                                JUGADA #{String(ticket.id).padStart(5, '0')}
                            </div>
                            <div className="ticket-body-sm">
                                <div className="aciertos-sm">{ticket.aciertos ?? 0} ACIERTOS</div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--color-primario)', marginTop: '4px' }}>
                                    Hacé clic para ver detalle
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </section>
    );
}
