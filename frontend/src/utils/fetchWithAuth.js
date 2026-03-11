/**
 * fetchWithAuth.js
 * Wrapper de fetch que agrega automáticamente el JWT en el header Authorization.
 * Si el servidor responde 401 (token expirado o inválido), limpia la sesión y
 * redirige al login recargando la página.
 */

export async function fetchWithAuth(url, options = {}) {
    const token = sessionStorage.getItem('jwt_token');

    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
        };
    }

    const response = await fetch(url, options);

    // Si el token expiró o es inválido, cerrar sesión automáticamente
    if (response.status === 401) {
        sessionStorage.removeItem('jwt_token');
        sessionStorage.removeItem('sabes_usuario');
        window.location.reload();
        // Retornar la respuesta igual para que el llamador pueda manejarla si quiere
    }

    return response;
}
