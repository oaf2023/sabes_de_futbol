import React from 'react';

export default function PerfilJugador({ usuario, onLogout, onAbrirCuenta }) {
    if (!usuario) return null;

    return (
        <section className="carnet-socio-classic">
            <div className="carnet-header">
                <h2>CARNET DE SOCIO</h2>
                <button className="btn-mi-cuenta-header" onClick={onAbrirCuenta}>
                    Mi Cuenta
                </button>
                <div className="linea-subrayado"></div>
            </div>

            <div className="carnet-content">
                <div className="col-foto">
                    <div className="foto-marco">
                        <img
                            src={usuario.foto_selfie || "https://via.placeholder.com/100x120?text=Socio"}
                            alt="Socio"
                            onError={(e) => { e.target.src = 'https://via.placeholder.com/100x120?text=Socio'; }}
                        />
                    </div>
                </div>
                <div className="col-datos">
                    <p className="dato-item"><strong>Socio:</strong> {usuario.dni}</p>
                    <p className="dato-item"><strong>Nombre:</strong> {usuario.nombre}</p>
                    <p className="dato-item"><strong>Pais:</strong> Argentina</p>
                </div>
            </div>

            <div className="carnet-actions">
                <button className="btn-jugadas-classic" onClick={() => {}}>
                    MIS JUGADAS<br />(HISTORIAL)
                </button>
                <button className="btn-logout-classic" onClick={onLogout}>
                    Cerrar<br />Sesión
                </button>
            </div>

            <div className={`carnet-status-banner ${usuario.completado === 'SI' ? 'status-valido' : 'status-pendiente'}`}>
                {usuario.completado === 'SI' ? '✓ DATOS COMPLETOS' : '⚠ DATOS INCOMPLETOS'}
            </div>
            
            {usuario.completado === 'NO' && (
                <div className="aviso-datos-incompletos">
                    Mientras los datos estén INCOMPLETOS no podrá reclamar el cambio de las fichas ganadas, SOLO podrá adquirir y realizar jugadas.
                </div>
            )}
        </section>
    );
}
