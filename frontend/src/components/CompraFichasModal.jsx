import React from 'react';

export default function CompraFichasModal({ onClose, onComprar }) {
    const paquetes = [
        { id: 'starter', nombre: 'STARTER', fichas: 5, precio: 1000 },
        { id: 'normal', nombre: 'NORMAL', fichas: 12, precio: 2000 },
        { id: 'pro', nombre: 'PRO', fichas: 30, precio: 4500 }
    ];

    return (
        <div id="modal-compra-fichas" className="modal-absolute">
            <div className="compra-fichas-card card-retro">
                <h3>COMPRAR FICHAS</h3>
                <p>Elegí un paquete para seguir jugando:</p>

                <div className="paquetes-container">
                    {paquetes.map(p => (
                        <div 
                            key={p.id} 
                            className={`paquete-item card-retro ${p.id === 'normal' ? 'selected' : ''}`}
                            onClick={() => onComprar(p.id)}
                        >
                            <span className="paquete-titulo">{p.nombre}</span>
                            <span className="paquete-fichas">{p.fichas} FICHAS</span>
                            <span className="paquete-precio">$ {p.precio.toLocaleString()}</span>
                        </div>
                    ))}
                </div>

                <p className="nota-pago">Serás redirigido a Mercado Pago para completar la operación.</p>

                <button className="btn-retro-sm" onClick={onClose} style={{ marginTop: '20px' }}>
                    CANCELAR
                </button>
            </div>
        </div>
    );
}
