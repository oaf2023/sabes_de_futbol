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
                    <p className="dato-item"><strong>Socio:</strong> {usuario.numero_de_socio}</p>
                    <p className="dato-item"><strong>Usuario:</strong> {usuario.nombre_de_usuario}</p>
                    <p className="dato-item"><strong>Nombre:</strong> {usuario.nombre || 'Sin completar'}</p>
                </div>
            </div>

            <div className="carnet-actions">
                <button className={`btn-jugadas-classic ${(usuario.fichas_ganadas || 0) < 50000 ? 'btn-canje-bloqueado' : ''}`} 
                        onClick={() => {
                            if ((usuario.fichas_ganadas || 0) < 50000) {
                                alert("⚠️ No estás en condiciones de canje (mínimo 50.000 fichas ganadas).");
                            } else {
                                // Lógica de canje
                            }
                        }}>
                    CANJEAR<br />PREMIOS
                </button>
                <button className="btn-logout-classic" onClick={onLogout}>
                    Cerrar<br />Sesión
                </button>
            </div>

            <div className={`carnet-status-banner status-valido`}>
                Socio Activo
            </div>

            {(usuario.fichas || 0) < 2500 && (
                <div className="aviso-fichas-insuficientes">
                    ⚠️ Fichas insuficientes
                </div>
            )}
        </section>
    );
}
