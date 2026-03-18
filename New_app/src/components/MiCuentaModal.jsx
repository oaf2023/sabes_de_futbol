import React, { useState } from 'react';
import { fetchWithAuth } from '../utils/fetchWithAuth';

export default function MiCuentaModal({ usuario, onClose, onActualizar }) {
    const [verificado, setVerificado] = useState(false);
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    // Estados para edición
    const [formData, setFormData] = useState({
        nombre: usuario.nombre || '',
        telefono: usuario.telefono || '',
        direccion: usuario.direccion || '',
        fecha_nac: usuario.fecha_nac || '',
        email: usuario.email || ''
    });
    const [fotos, setFotos] = useState({
        foto_dni_frente: null,
        foto_dni_dorso: null,
        foto_selfie: null
    });

    const handleVerificar = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const resp = await fetchWithAuth('/api/usuario/verificar-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            const data = await resp.json();
            if (resp.ok) {
                setVerificado(true);
            } else {
                setError(data.error || 'Acceso denegado');
            }
        } catch (err) {
            setError('Error de conexión');
        } finally {
            setLoading(false);
        }
    };

    const handleGuardar = async (e) => {
        e.preventDefault();
        setLoading(true);
        const data = new FormData();
        // No se envía el DNI en el body — el backend lo obtiene del JWT
        Object.keys(formData).forEach(key => data.append(key, formData[key]));
        Object.keys(fotos).forEach(key => {
            if (fotos[key]) data.append(key, fotos[key]);
        });

        try {
            const resp = await fetchWithAuth('/api/usuario/actualizar', {
                method: 'POST',
                body: data
            });
            const resData = await resp.json();
            if (resp.ok) {
                onActualizar(resData.usuario);
                onClose();
            } else {
                setError(resData.error || 'Error al actualizar');
            }
        } catch (err) {
            setError('Error al conectar con el servidor');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content card-madera" style={{ maxWidth: '500px', width: '90%' }}>
                <div className="ticket-header">
                    <h2>GESTIÓN DE CUENTA</h2>
                    <button className="btn-close" onClick={onClose}>X</button>
                </div>

                {!verificado ? (
                    <form onSubmit={handleVerificar} className="auth-form" style={{ padding: '20px' }}>
                        <p style={{ marginBottom: '15px', textAlign: 'center' }}>
                            Por seguridad, ingresá tu contraseña para acceder a tus datos.
                        </p>
                        <div className="form-group">
                            <label>Contraseña:</label>
                            <input 
                                type="password" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="retro-input"
                            />
                        </div>
                        {error && <p className="error-msg">{error}</p>}
                        <button type="submit" className="btn-retro-lg" disabled={loading}>
                            {loading ? 'VERIFICANDO...' : 'VERIFICAR IDENTIDAD'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleGuardar} className="auth-form" style={{ padding: '20px', maxHeight: '70vh', overflowY: 'auto' }}>
                        <div className="form-group">
                            <label>Nombre y Apellido:</label>
                            <input 
                                type="text" 
                                value={formData.nombre}
                                onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                                className="retro-input"
                            />
                        </div>
                        <div className="form-group">
                            <label>Teléfono:</label>
                            <input 
                                type="text" 
                                value={formData.telefono}
                                onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                                className="retro-input"
                            />
                        </div>
                        <div className="form-group">
                            <label>Dirección:</label>
                            <input 
                                type="text" 
                                value={formData.direccion}
                                onChange={(e) => setFormData({...formData, direccion: e.target.value})}
                                className="retro-input"
                            />
                        </div>
                        <div className="form-group">
                            <label>Fecha de Nacimiento:</label>
                            <input 
                                type="date" 
                                value={formData.fecha_nac}
                                onChange={(e) => setFormData({...formData, fecha_nac: e.target.value})}
                                className="retro-input"
                            />
                        </div>

                        <div style={{ marginTop: '15px', borderTop: '1px dashed #666', paddingTop: '10px' }}>
                            <p style={{ fontSize: '0.8rem', marginBottom: '8px' }}>Actualizar Fotos (opcional):</p>
                            <div className="form-group-file">
                                <label>DNI Frente:</label>
                                <input type="file" onChange={(e) => setFotos({...fotos, foto_dni_frente: e.target.files[0]})} />
                            </div>
                            <div className="form-group-file">
                                <label>DNI Dorso:</label>
                                <input type="file" onChange={(e) => setFotos({...fotos, foto_dni_dorso: e.target.files[0]})} />
                            </div>
                            <div className="form-group-file">
                                <label>Foto Selfie:</label>
                                <input type="file" onChange={(e) => setFotos({...fotos, foto_selfie: e.target.files[0]})} />
                            </div>
                        </div>

                        {error && <p className="error-msg">{error}</p>}
                        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                            <button type="submit" className="btn-retro-lg" style={{ background: '#239b56' }} disabled={loading}>
                                {loading ? 'GUARDANDO...' : 'GUARDAR CAMBIOS'}
                            </button>
                            <button type="button" className="btn-retro-lg" style={{ background: '#922b21' }} onClick={onClose}>
                                CANCELAR
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
