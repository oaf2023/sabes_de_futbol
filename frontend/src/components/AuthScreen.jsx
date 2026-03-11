import React, { useState } from 'react';

export default function AuthScreen({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [aceptarTerminos, setAceptarTerminos] = useState(false);

    const [formData, setFormData] = useState({
        dni: '',
        password: '',
        nombre: '',
        telefono: '',
        direccion: '',
        fecha_nac: '',
        email: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!isLogin) {
            if (formData.password !== formData.confirmPassword) {
                setError("Las contraseñas no coinciden.");
                return;
            }
            if (!aceptarTerminos) {
                setError("Debes aceptar los términos y condiciones para registrarte.");
                return;
            }
        }

        setLoading(true);
        setError(null);
        setSuccess(null);

        const endpoint = isLogin ? '/api/login' : '/api/register';

        try {
            let resp;
            if (isLogin) {
                resp = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dni: formData.dni, password: formData.password })
                });
            } else {
                const fd = new FormData();
                fd.append('dni', formData.dni);
                fd.append('password', formData.password);
                fd.append('nombre', formData.nombre);
                fd.append('telefono', formData.telefono);
                fd.append('direccion', formData.direccion);
                fd.append('reg-nacimiento', formData.fecha_nac);
                fd.append('email', formData.email);

                const fileInputs = e.target.querySelectorAll('input[type="file"]');
                fileInputs.forEach(input => {
                    if (input.files[0]) fd.append(input.name, input.files[0]);
                });

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
                    setSuccess("¡Socio registrado! Ya podés ingresar.");
                    setTimeout(() => setIsLogin(true), 2000);
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
            <div className="login-card card-retro">
                <div className="boleta-header">
                    <h1 className="logo-sabes">SABES DE FUTBOL</h1>
                    <div className="boleta-numero">CARNET DE SOCIO</div>
                </div>

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
                {success && <p className="login-error" style={{ color: 'var(--color-acento)' }}>{success}</p>}

                {isLogin ? (
                    <form className="login-form" onSubmit={handleSubmit}>
                        <label>Nº de Documento</label>
                        <input
                            name="dni"
                            type="text"
                            placeholder="Ej: 12345678"
                            required
                            value={formData.dni}
                            onChange={handleChange}
                            disabled={loading}
                        />
                        <label>Contraseña</label>
                        <input
                            name="password"
                            type="password"
                            placeholder="Tu clave secreta"
                            required
                            value={formData.password}
                            onChange={handleChange}
                            disabled={loading}
                        />
                        <button type="submit" className="btn-jugar" disabled={loading}>
                            {loading ? 'PROCESANDO...' : 'INGRESAR AL CLUB'}
                        </button>
                    </form>
                ) : (
                    <form className="login-form" onSubmit={handleSubmit}>
                        <label>Nº de Documento *</label>
                        <input name="dni" type="text" placeholder="Ej: 12345678" required value={formData.dni} onChange={handleChange} disabled={loading} />

                        <label>Teléfono</label>
                        <input name="telefono" type="tel" placeholder="Ej: 11 4321-8765" value={formData.telefono} onChange={handleChange} disabled={loading} />

                        <label>Correo Electrónico</label>
                        <input name="email" type="email" placeholder="ejemplo@correo.com" value={formData.email} onChange={handleChange} disabled={loading} />

                        <label>Fecha de Nacimiento</label>
                        <input name="fecha_nac" type="date" value={formData.fecha_nac} onChange={handleChange} disabled={loading} />

                        <label>Nombre y Apellido *</label>
                        <input name="nombre" type="text" placeholder="Juan Pérez" required value={formData.nombre} onChange={handleChange} disabled={loading} />

                        <label>Dirección</label>
                        <input name="direccion" type="text" placeholder="Calle, Nro, Provincia" value={formData.direccion} onChange={handleChange} disabled={loading} />

                        <label>Contraseña *</label>
                        <input name="password" type="password" placeholder="Elegí una clave" required value={formData.password} onChange={handleChange} disabled={loading} />
                        
                        <label>Confirmar Contraseña *</label>
                        <input name="confirmPassword" type="password" placeholder="Repetí tu clave" required value={formData.confirmPassword} onChange={handleChange} disabled={loading} />

                        <label>Foto DNI (Frente)</label>
                        <input name="foto_dni_frente" type="file" accept="image/*" disabled={loading} />

                        <label>Foto DNI (Dorso)</label>
                        <input name="foto_dni_dorso" type="file" accept="image/*" disabled={loading} />

                        <label>Foto Personal (Selfie)</label>
                        <input name="foto_selfie" type="file" accept="image/*" disabled={loading} />

                        <div className="terminos-contenedor">
                            <div className="terminos-box">
                                <h4 style={{ margin: '0 0 5px 0', fontSize: '10px', color: '#666' }}>TÉRMINOS Y CONDICIONES</h4>
                                <p><strong>1. Aceptación del Acuerdo y Requisito de Edad</strong><br/>
                                Estos Términos y Condiciones constituyen un acuerdo legal vinculante entre usted y el proveedor de la aplicación. <strong>Para poder crear una cuenta, acceder y utilizar esta aplicación, usted debe ser un adulto, es decir, haber alcanzado la mayoría de edad legal en su jurisdicción o país de residencia</strong> (al menos 18 años en la mayoría de los países de América Latina).</p>
                                
                                <p><strong>2. Licencia de Uso (La aplicación no se vende)</strong><br/>
                                <strong>Esta aplicación y sus contenidos se le otorgan bajo licencia, no se le venden</strong>. Esto significa que usted no adquiere ningún derecho de propiedad sobre la aplicación ni sobre sus contenidos digitales.</p>
                                
                                <p>Bajo esta licencia, <strong>usted no puede</strong>:</p>
                                <ul>
                                    <li>Vender, alquilar, arrendar, redistribuir, ceder o sublicenciar la aplicación.</li>
                                    <li>Realizar ingeniería inversa, descompilar, desensamblar, modificar o crear obras derivadas de la aplicación.</li>
                                    <li>Utilizar la aplicación de manera que infrinja los derechos de propiedad intelectual de terceros.</li>
                                </ul>

                                <p><strong>3. Propiedad Intelectual</strong><br/>
                                Nosotros poseemos y nos reservamos todos los derechos sobre la aplicación, incluyendo todo el código informático, diseños, gráficos, audios e interfaz.</p>

                                <p><strong>4. Reglas de Conducta del Usuario</strong><br/>
                                Esperamos que utilice la aplicación de manera legal y respetuosa. Nos reservamos el derecho de tomar medidas disciplinarias si usted participa en conductas prohibidas como actividades ilegales, fraude, acoso o uso de trampas (cheats).</p>

                                <p><strong>5. Cancelación y Suspensión de la Cuenta</strong><br/>
                                <strong>Podemos cancelar, suspender o limitar su acceso a la aplicación de manera inmediata si determinamos que ha incumplido estos Términos y Condiciones</strong>.</p>

                                <p><strong>6. Renuncia de Garantías ("Tal Cual")</strong><br/>
                                <strong>La aplicación se proporciona "tal cual" (as is) y "según disponibilidad"</strong>, sin garantías de ningún tipo.</p>

                                <p><strong>7. Limitación de Responsabilidad</strong><br/>
                                En la medida máxima permitida por las leyes aplicables, ni la empresa ni sus filiales serán responsables por daños indirectos, incidentales o consecuentes que surjan del uso o la imposibilidad de uso de la aplicación.</p>

                                <p><strong>8. Privacidad y Uso de Datos</strong><br/>
                                Al utilizar esta aplicación, usted acepta que recopilemos e información técnica y datos personales de acuerdo con nuestra <strong>Política de Privacidad</strong>.</p>

                                <p><strong>9. Legislación Aplicable y Resolución de Disputas</strong><br/>
                                Las leyes de su país de residencia en América Latina pueden otorgarle derechos irrenunciables. Estos Términos no pretenden excluir ninguno de esos derechos legales imperativos.</p>
                            </div>
                            <label className="terminos-aceptacion">
                                <input 
                                    type="checkbox" 
                                    checked={aceptarTerminos} 
                                    onChange={(e) => setAceptarTerminos(e.target.checked)}
                                    disabled={loading}
                                />
                                Acepto los Términos y Condiciones de Uso
                            </label>
                        </div>

                        <button 
                            type="submit" 
                            className="btn-jugar" 
                            disabled={loading || !aceptarTerminos}
                            style={{ opacity: (loading || !aceptarTerminos) ? 0.6 : 1 }}
                        >
                            {loading ? 'PROCESANDO...' : 'SELLAR REGISTRO'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}
