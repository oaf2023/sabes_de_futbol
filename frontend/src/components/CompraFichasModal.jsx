import React, { useState } from 'react';

const COSTO_JUGADA = 2500;

export default function CompraFichasModal({ fichasActuales = 0, onClose, onComprar }) {
    const faltantes = Math.max(COSTO_JUGADA - fichasActuales, 1);
    const [cantidad, setCantidad] = useState(faltantes);

    const handleCambio = (e) => {
        const val = parseInt(e.target.value, 10);
        if (!isNaN(val) && val >= 1) setCantidad(val);
        else if (e.target.value === '') setCantidad('');
    };

    const handleConfirmar = () => {
        const cant = parseInt(cantidad, 10);
        if (!cant || cant < 1) return;
        onComprar(cant);
    };

    const cantidadValida = parseInt(cantidad, 10) >= 1;
    const totalARS = cantidadValida ? parseInt(cantidad, 10).toLocaleString('es-AR') : '—';

    return (
        <div className="modal-overlay">
            <div className="compra-fichas-card card-retro">
                <h3 className="compra-fichas-titulo">COMPRAR FICHAS</h3>

                <div className="compra-fichas-info">
                    <div className="compra-info-row">
                        <span className="compra-info-lbl">TUS FICHAS</span>
                        <span className="compra-info-val">{fichasActuales.toLocaleString('es-AR')}</span>
                    </div>
                    <div className="compra-info-row">
                        <span className="compra-info-lbl">PARA JUGAR</span>
                        <span className="compra-info-val compra-info-val--rojo">{COSTO_JUGADA.toLocaleString('es-AR')}</span>
                    </div>
                </div>

                <div className="compra-fichas-input-section">
                    <label className="compra-input-lbl">¿CUÁNTAS FICHAS QUERÉS?</label>
                    <input
                        type="number"
                        min="1"
                        value={cantidad}
                        onChange={handleCambio}
                        className="fichas-input"
                        autoFocus
                    />
                </div>

                <div className="fichas-precio-preview">
                    <span className="precio-preview-lbl">TOTAL A PAGAR</span>
                    <span className="precio-preview-val">$ {totalARS}</span>
                    <span className="precio-preview-nota">1 ficha = $ 1 ARS</span>
                </div>

                <p className="nota-pago">Serás redirigido a Mercado Pago para completar la operación.</p>

                <div className="compra-fichas-btns">
                    <button
                        className="btn-retro-sm btn-confirmar"
                        onClick={handleConfirmar}
                        disabled={!cantidadValida}
                    >
                        CONFIRMAR
                    </button>
                    <button className="btn-retro-sm btn-cancelar" onClick={onClose}>
                        CANCELAR
                    </button>
                </div>
            </div>
        </div>
    );
}
