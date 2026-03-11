/*
Nombre: api.js
Fecha: 2026-03-04
Versión: 2.0
Creador: OAF
Propósito: Módulo de servicios para el frontend.
Funcionamiento: Centraliza las llamadas AJAX fetch al backend Flask (Login, Partidos, Jugadas).
Fuentes de datos: Endpoint base dinámico (localhost o dominio actual).
Ejemplo de uso: importado en index.html o referenciado antes de script.js.
*/

// Detectar si estamos en local o en producción
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE_URL = isLocal
    ? 'http://127.0.0.1:5000'
    : ''; // En producción usar rutas relativas para evitar líos de dominios


/**
 * Helper genérico para llamadas JSON al API.
 * Retorna { ok, data, error }
 */
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) options.body = JSON.stringify(body);

        const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await res.json();

        if (!res.ok) {
            return { ok: false, error: data.error || 'Error del servidor', data };
        }
        return { ok: true, data };
    } catch (err) {
        return { ok: false, error: '⚠️ No se pudo conectar al servidor. ¿Está corriendo el backend?' };
    }
}

/**
 * Helper para formularios con archivos (multipart/form-data)
 */
async function apiUpload(endpoint, formData) {
    try {
        const res = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,   // No Content-Type header — el browser lo pone solo con el boundary
        });
        const data = await res.json();
        if (!res.ok) {
            return { ok: false, error: data.error || 'Error del servidor', data };
        }
        return { ok: true, data };
    } catch (err) {
        return { ok: false, error: '⚠️ No se pudo conectar al servidor.' };
    }
}

// ---------------------------------------------------------------------------
// Funciones específicas de la API
// ---------------------------------------------------------------------------

/** Registrar nuevo usuario */
async function apiRegister(formData) {
    return apiUpload('/api/register', formData);
}

/** Login del usuario */
async function apiLogin(dni, password) {
    return apiCall('/api/login', 'POST', { dni, password });
}

/** Obtener partidos del sorteo actual */
async function apiGetPartidos() {
    return apiCall('/api/partidos', 'GET');
}

/** Guardar jugadas (múltiples) */
async function apiGuardarJugadas(dni, jugadas) {
    return apiCall('/api/jugada', 'POST', { dni, jugadas });
}

/** Obtener fichas del usuario */
async function apiGetFichas(dni) {
    return apiCall(`/api/usuario/${dni}/fichas`, 'GET');
}

/** Ejecutar el sorteo */
async function apiSortear(jugadaId) {
    return apiCall('/api/sortear', 'POST', { jugada_id: jugadaId });
}

/** Obtener historial del usuario */
async function apiHistorial(dni) {
    return apiCall(`/api/historial/${dni}`, 'GET');
}

/** Iniciar proceso de pago real (Mercado Pago) */
async function apiIniciarPago(dni, paquete) {
    return apiCall('/api/iniciar-pago', 'POST', { dni, paquete });
}

/** Verificar estado de un pago por ID de preferencia */
async function apiGetPagoEstado(preferenceId) {
    return apiCall(`/api/pago-estado/${preferenceId}`, 'GET');
}

/** Obtener detalle completo de una jugada específica */
async function apiGetDetalleJugada(jugadaId) {
    return apiCall(`/api/jugada/${jugadaId}`, 'GET');
}
