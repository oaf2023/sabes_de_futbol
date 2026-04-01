import React, { useState, useEffect } from 'react';
import '../App.css';

const AuthScreen = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [viewModal, setViewModal] = useState(null);
    const [stats, setStats] = useState(null);
    
    // El contador de socios (Real + 1000)
    const socioCount = stats?.total_socios || '1005';

    const [formData, setFormData] = useState({
        socio: '',
        password: '',
        usuario: '',
        nombre: '',
        confirmPassword: ''
    });

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch('/api/stats-public');
                if (res.ok) {
                    const data = await res.json();
                    setStats(data);
                }
            } catch (err) {
                console.error("Error stats", err);
            }
        };
        fetchStats();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (!isLogin && formData.password !== formData.confirmPassword) {
            setError("Las contraseñas no coinciden");
            setLoading(false);
            return;
        }

        try {
            const endpoint = isLogin ? '/api/login' : '/api/register';
            let resp;
            
            if (isLogin) {
                resp = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        socio: formData.socio,
                        password: formData.password
                    })
                });
            } else {
                const fd = new FormData();
                fd.append('nombre_de_usuario', formData.usuario);
                fd.append('nombre', formData.nombre);
                fd.append('password', formData.password);
                
                resp = await fetch(endpoint, {
                    method: 'POST',
                    body: fd
                });
            }

            const data = await resp.json();

            if (resp.ok) {
                if (isLogin) {
                    onLogin(data.usuario, data.token);
                } else {
                    const nro = data.usuario.numero_de_socio;
                    setSuccess(`¡Socio registrado! Tu número es: ${nro}. Anotalo para ingresar.`);
                    setTimeout(() => {
                        setIsLogin(true);
                        setFormData(prev => ({ ...prev, socio: nro.toString() }));
                        setSuccess(null);
                    }, 5000);
                }
            } else {
                setError(data.error || "Error en el carnet");
            }
        } catch (err) {
            setError("Error de conexión");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div id="pantalla-login" className="login-overlay">
            <div className="fichas-fondo">
                {Array.from({ length: 12 }).map((_, i) => (
                    <img
                        key={i}
                        src="/logo.png"
                        alt=""
                        className="ficha-cayendo"
                        style={{
                            left: `${(i * 8.5) % 100}%`,
                            width: `${48 + (i % 3) * 20}px`,
                            height: `${48 + (i % 3) * 20}px`,
                            animationDuration: `${4 + (i % 5)}s`,
                            animationDelay: `${(i * 0.7) % 5}s`,
                        }}
                    />
                ))}
            </div>

            <div className="login-card card-retro">
                {/* MODALES TIPO "OVERLAY INTERNO" - Mejorados estilo GitHub */}
                {viewModal === 'reglamento' && (
                    <div className="login-card-modal">
                        <div className="modal-header-retro">
                            <h2 style={{ fontSize: '1.2rem', margin: 0 }}>📜 REGLAMENTO</h2>
                            <button className="btn-cerrar-retro" type="button" onClick={() => setViewModal(null)}>VOLVER</button>
                        </div>
                        <div className="modal-body-retro">
                            <p style={{ fontWeight: 'bold', borderBottom: '1px solid #ccc', paddingBottom: '5px' }}>REGLAMENTO DEL JUEGO</p>
                            <p>1. Marcá resultados de una fecha de primera división (Local, Empate o Visitante).</p>
                            <p>2. Por partido se marca un solo resultado.</p>
                            <p>3. La cantidad de partidos depende del fixture.</p>
                            <p>4. Si un partido se suspende, la fecha no se cierra hasta tener el resultado final.</p>
                            <p>5. Existen 4 niveles de acierto: Total, Total-1, Total-2 y Total-3.</p>
                            <p>6. El recupero de fichas se muestra en el Pozo Acumulado.</p>
                            <p>7. Podés jugar todas las boletas que desees.</p>
                            <p>8. Cada boleta canjea 2.500 fichas (1 ficha del club).</p>
                            <p>9. Siempre debe tener el mínimo de 2.500 fichas para jugar.</p>
                            <p>10. No se permite llenar boletas de la fecha en curso.</p>
                            <p>11. Se permiten boletas hasta 3 horas antes del primer partido.</p>
                            <p>12. Se pueden llenar boletas de la próxima fecha si existe.</p>
                            <p>13. El recupero de fichas es automático al finalizar los partidos.</p>
                            <p>14. El canje se habilita al superar las 50.000 fichas.</p>
                            <p>15. Al superar las 50.000 fichas se activa el botón de canje automático.</p>
                            <p>16. Solo se canjean fichas obtenidas por aciertos.</p>
                            <p>17. El canje es exclusivo para lo ganado en jugadas.</p>
                            <p>18. Se muestra la cantidad de usuarios ganadores (sin nombres ni datos).</p>
                            <p>19. El sistema notifica al usuario que acertó para su acreditación.</p>
                            <p style={{ marginTop: '20px', fontStyle: 'italic', opacity: 0.7, textAlign: 'center' }}>"En el fútbol como en la vida, el que sabe, sabe."</p>
                        </div>
                    </div>
                )}

                {viewModal === 'comojugar' && (
                    <div className="login-card-modal">
                        <div className="modal-header-retro">
                            <h2 style={{ fontSize: '1.2rem', margin: 0 }}>⚽ GUÍA DEL SOCIO</h2>
                            <button className="btn-cerrar-retro" type="button" onClick={() => setViewModal(null)}>CERRAR</button>
                        </div>
                        <div className="modal-body-retro">
                            <p style={{ textAlign: 'center', color: 'var(--color-primario)', fontWeight: 'bold' }}>¡Paso a paso para ser un experto!</p>
                            <p><strong>1. CARNET:</strong> Ingresá con tu número de socio y contraseña para acceder al club.</p>
                            <p><strong>2. LA BOLETA:</strong> Verás los partidos de la fecha. Marcá L (Local), E (Empate) o V (Visitante).</p>
                            <p><strong>3. SELLADO:</strong> Revisa tu jugada y hacé clic en "JUEGA BOLETA". Cada una consume 2.500 fichas.</p>
                            <p><strong>4. SEGUIMIENTO:</strong> Mirá en tiempo real cómo van tus aciertos durante el transcurso de la fecha.</p>
                            <p><strong>5. PREMIOS:</strong> Si ganás, tus fichas se acreditan solas. Al llegar a 50.000 puntos, ¡activás el canje!</p>
                            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#eef', border: '1px dashed #99f', fontSize: '0.8rem' }}>
                                💡 <strong>Dato clave:</strong> Podés jugar todas las boletas que quieras de la próxima fecha antes de que comience el primer partido.
                            </div>
                        </div>
                    </div>
                )}

                <div className="login-logo-wrap">
                    <img src="/logo.png" alt="Sabes de Fútbol" className="login-logo" />
                </div>
                
                <div className="boleta-numero" style={{ textAlign: 'center', marginBottom: '8px' }}>CARNET DE SOCIO</div>

                {isLogin && (
                    <div className="login-stats-box">
                        <div className="stat-unica-linea">
                            <span>SOCIOS REGISTRADOS:</span>
                            <span className="stat-valor-destacado">{socioCount}</span>
                        </div>
                    </div>
                )}

                <div className="login-tabs">
                    <button
                        className={`tab-btn ${isLogin ? 'active' : ''}`}
                        onClick={() => { setIsLogin(true); setError(null); }}
                    >
                        INGRESAR
                    </button>
                    <button
                        className={`tab-btn ${!isLogin ? 'active' : ''}`}
                        onClick={() => { setIsLogin(false); setError(null); }}
                    >
                        NUEVO SOCIO
                    </button>
                </div>

                {error && <p className="login-error">{error}</p>}
                {success && <p className="login-error" style={{ color: 'var(--color-acento)', backgroundColor: 'rgba(0,0,0,0.8)', padding: '10px', borderRadius: '5px' }}>{success}</p>}

                <form className="login-form" onSubmit={handleSubmit}>
                    {isLogin ? (
                        <>
                            <label>Nº de Socio o Usuario</label>
                            <input
                                name="socio"
                                type="text"
                                placeholder="Ej: 1001"
                                required
                                value={formData.socio}
                                onChange={handleChange}
                                disabled={loading}
                            />
                            <label>Contraseña</label>
                            <input
                                name="password"
                                type="password"
                                placeholder="..."
                                required
                                value={formData.password}
                                onChange={handleChange}
                                disabled={loading}
                            />
                            <button type="submit" className="btn-jugar" disabled={loading}>
                                {loading ? 'ESPERE...' : 'INGRESAR AL CLUB'}
                            </button>
                        </>
                    ) : (
                        <>
                            <label>Usuario *</label>
                            <input name="usuario" type="text" placeholder="Ej: juan_futbol" required value={formData.usuario} onChange={handleChange} disabled={loading} />
                            <label>Nombre Completo *</label>
                            <input name="nombre" type="text" placeholder="Juan Pérez" required value={formData.nombre} onChange={handleChange} disabled={loading} />
                            <label>Contraseña *</label>
                            <input name="password" type="password" required value={formData.password} onChange={handleChange} disabled={loading} />
                            <label>Repetir Contraseña *</label>
                            <input name="confirmPassword" type="password" required value={formData.confirmPassword} onChange={handleChange} disabled={loading} />
                            <button type="submit" className="btn-jugar" disabled={loading}>
                                {loading ? 'REGISTRANDO...' : 'OBTENER CARNET'}
                            </button>
                        </>
                    )}
                    
                    {/* BOTONES DENTRO DEL CARNET */}
                    <div className="login-card-footer">
                        <button 
                            className="btn-retro-circle btn-reglamento-card" 
                            type="button"
                            onClick={() => setViewModal('reglamento')}
                        >
                            📜 REGLAS
                        </button>
                        <button 
                            className="btn-retro-circle btn-comojugar-card" 
                            type="button"
                            onClick={() => setViewModal('comojugar')}
                        >
                            ⚽ GUÍA
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AuthScreen;
