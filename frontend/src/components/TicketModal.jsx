import React from 'react';

export default function TicketModal({ ticket, dni, onClose }) {
    if (!ticket) return null;

    // Formatear nro de fecha
    const nroFecha = ticket.nro_fecha || "00000";
    const jugadaId = String(ticket.id || 0).padStart(5, '0');
    const socioDni = dni || ticket.usuario_dni || "XXXXXXXX";
    const fechaHora = ticket.fecha || ticket.fecha_hora || new Date().toLocaleString();

    const handleDescargar = async () => {
        const area = document.getElementById('ticket-capture-area');
        if (!area || !window.html2canvas) {
            console.error("html2canvas no cargado o área no encontrada");
            return;
        }

        try {
            const filename = `ticket_sabes_${socioDni}_${jugadaId}.png`;
            const canvas = await window.html2canvas(area, {
                backgroundColor: '#fdf5e6',
                scale: 2,
                useCORS: true,
                logging: false
            });

            const link = document.createElement('a');
            link.download = filename;
            link.href = canvas.toDataURL("image/png");
            link.click();
        } catch (err) {
            console.error("Error capturando ticket:", err);
            alert("Error al generar la imagen. Intentá de nuevo.");
        }
    };

    return (
        <div id="container-ticket-modal" className="modal-overlay">
            <button
                className="btn-cerrar-modal"
                onClick={onClose}
                style={{
                    position: 'fixed',
                    top: '20px',
                    right: '25px',
                    background: 'transparent',
                    border: 'none',
                    color: 'white',
                    fontSize: '3rem',
                    cursor: 'pointer',
                    zIndex: 2100
                }}
            >
                ×
            </button>

            <div className="ticket-boleta card-retro" id="ticket-capture-area" style={{ margin: '0' }}>
                <div className="ticket-header">
                    <h3>SABES DE FUTBOL</h3>
                    <p>COMPROBANTE DE JUGADA</p>
                    <div id="ticket-id" className="ticket-num">
                        JUGADA #{jugadaId}
                    </div>
                    {ticket.aciertos !== undefined && ticket.aciertos !== "?" && (
                        <div style={{ color: 'var(--color-error)', fontWeight: 'bold', fontSize: '1.1rem', marginTop: '5px' }}>
                            {ticket.aciertos} ACIERTOS
                        </div>
                    )}
                </div>
                <hr style={{ border: 'none', borderTop: '1px dashed #999', margin: '10px 0' }} />
                <div id="ticket-datos-usuario">
                    <p>Socio: <span id="t-dni">{socioDni}</span></p>
                    <p>Fecha: <span id="t-fecha">{parseInt(nroFecha)}</span> - <span id="t-timestamp">{fechaHora}</span></p>
                </div>
                <hr style={{ border: 'none', borderTop: '1px dashed #999', margin: '10px 0' }} />
                <div id="ticket-lista-partidos" className="ticket-lista">
                    {ticket.partidos && ticket.partidos.map((p, i) => (
                        <p key={i}>
                            <span>{i + 1}. {p.nombre}</span>
                            <b>{p.seleccion || p.resultado}</b>
                        </p>
                    ))}
                </div>
                <hr style={{ border: 'none', borderTop: '1px dashed #999', margin: '10px 0' }} />
                <div className="ticket-footer no-print">
                    <p style={{ margin: '10px 0', fontWeight: 'bold' }}>¡MUCHA SUERTE!</p>
                    <button
                        onClick={handleDescargar}
                        className="btn-retro-sm"
                        style={{ width: '100%', marginBottom: '10px' }}
                    >
                        DESCARGAR IMAGEN (.PNG)
                    </button>
                    <button
                        onClick={onClose}
                        className="btn-retro-sm"
                        style={{ background: '#666', width: '100%' }}
                    >
                        VOLVER AL JUEGO
                    </button>
                </div>
            </div>
        </div>
    );
}
