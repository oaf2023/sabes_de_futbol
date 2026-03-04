import React, { useState } from 'react';

export default function AuthScreen({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);

    const handleSubmit = (e) => {
        e.preventDefault();
        // Simulate login or register
        onLogin({
            nombre: isLogin ? 'Jugador' : 'Nuevo Jugador',
            doc: '12345678'
        });
    };

    return (
        <div style={{
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            minHeight: '80vh', width: '100%'
        }}>
            <section className="card boleta-digital" style={{
                width: '500px', transform: 'rotate(0deg)', padding: '2rem'
            }}>
                <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    borderBottom: '2px dashed #ccc', paddingBottom: '10px', marginBottom: '20px'
                }}>
                    <h1 className="logo-sabes" style={{ fontFamily: 'var(--font-titulo)', color: 'var(--color-primario)', fontSize: '2.5rem', letterSpacing: '1px', textShadow: '2px 2px 0px rgba(0,0,0,0.1)' }}>SABES DE FUTBOL</h1>
                </div>

                <div style={{
                    position: 'absolute', top: '10%', right: '5%', transform: 'rotate(15deg)',
                    fontFamily: 'var(--font-titulo)', fontSize: '1.5rem', color: 'rgba(146, 43, 33, 0.2)',
                    pointerEvents: 'none', zIndex: 0, border: '2px dashed rgba(146, 43, 33, 0.2)',
                    padding: '5px', textAlign: 'center'
                }}>RESERVADO</div>

                <h2 style={{ fontFamily: 'var(--font-titulo)', textAlign: 'center', color: 'var(--color-primario)', marginBottom: '1rem' }}>
                    {isLogin ? 'INGRESO DE SOCIOS' : 'NUEVO AFILIADO'}
                </h2>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px', position: 'relative', zIndex: 1 }}>

                    {isLogin ? (
                        <>
                            <div className="input-group">
                                <label>Nº de Documento:</label>
                                <input type="text" required placeholder="Ej: 12345678" />
                            </div>
                            <div className="input-group">
                                <label>Clave / Contraseña:</label>
                                <input type="password" required placeholder="********" />
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="input-group">
                                <label>Nº de Documento:</label>
                                <input type="text" required placeholder="DNI Libreta Enrolamiento..." />
                            </div>
                            <div className="input-group">
                                <label>Dirección / Domicilio:</label>
                                <input type="text" required placeholder="Calle, Barrio, Provincia" />
                            </div>
                            <div className="input-group">
                                <label>Teléfono de Contacto:</label>
                                <input type="tel" required placeholder="Ej: 11 4321-8765" />
                            </div>
                            <div className="input-group">
                                <label>Correo Electrónico (Opcional):</label>
                                <input type="email" placeholder="ejemplo@correo.com" />
                            </div>
                            <div className="input-group">
                                <label>Fecha de Nacimiento:</label>
                                <input type="date" required style={{ fontFamily: 'var(--font-cuerpo)' }} />
                            </div>
                            <div className="input-group">
                                <label>Foto Documento (Frente):</label>
                                <input type="file" required accept="image/*" />
                            </div>
                            <div className="input-group">
                                <label>Foto Documento (Dorso):</label>
                                <input type="file" required accept="image/*" />
                            </div>
                            <div className="input-group">
                                <label>Foto Carnet (Selfie):</label>
                                <input type="file" required accept="image/*" />
                            </div>
                            <div className="input-group">
                                <label>Elegí una Contraseña:</label>
                                <input type="password" required />
                            </div>
                        </>
                    )}

                    <button type="submit" style={{
                        marginTop: '15px', padding: '15px', backgroundColor: 'var(--color-acento)',
                        color: 'var(--color-blanco)', border: 'none', fontFamily: 'var(--font-titulo)',
                        fontSize: '1.2rem', cursor: 'pointer', boxShadow: '4px 4px 0px rgba(0,0,0,0.2)', transition: 'all 0.1s'
                    }}>
                        {isLogin ? 'INGRESAR FICHAS' : 'SELLAR REGISTRO'}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '20px', position: 'relative', zIndex: 1 }}>
                    <button
                        type="button"
                        onClick={() => setIsLogin(!isLogin)}
                        style={{
                            background: 'none', border: 'none', color: 'var(--color-primario)',
                            fontFamily: 'var(--font-cuerpo)', textDecoration: 'underline', cursor: 'pointer',
                            fontSize: '0.9rem'
                        }}
                    >
                        {isLogin ? '¿No tenés carnet? Regístrate acá.' : '¿Ya sos vitalicio? Iniciá sesión.'}
                    </button>
                </div>

            </section>

            <style>{`
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .input-group label {
            font-weight: bold;
            font-size: 0.9rem;
            color: var(--color-primario);
        }
        .input-group input {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 2px;
            background-color: #fffaf0;
            font-family: var(--font-cuerpo);
        }
        .input-group input:focus {
            outline: 2px solid var(--color-acento);
        }
      `}</style>
        </div>
    );
}
