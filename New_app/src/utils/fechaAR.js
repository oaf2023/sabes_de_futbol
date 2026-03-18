/**
 * Convierte una fecha ISO (UTC del backend) a string legible en zona Argentina.
 * Uso: fechaAR('2026-03-13T20:00:00') → "13/03/2026 17:00"
 */
export function fechaAR(isoString, conHora = true) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    if (isNaN(d)) return isoString;
    const opts = {
        timeZone: 'America/Argentina/Buenos_Aires',
        day: '2-digit', month: '2-digit', year: 'numeric',
    };
    if (conHora) {
        opts.hour = '2-digit';
        opts.minute = '2-digit';
    }
    return d.toLocaleString('es-AR', opts);
}
