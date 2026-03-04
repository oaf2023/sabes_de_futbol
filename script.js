/*
Nombre: script.js
Fecha: 2026-03-04
Versión: 2.1
Creador: OAF
Propósito: Lógica principal del frontend (auth, jugadas, animaciones, renderizado dinámico).
Funcionamiento: Maneja la interacción del usuario, el flujo del juego, la comunicación con el API y las animaciones de la ruleta.
Fuentes de datos: Se comunica con el backend Flask a través de api.js.
Ejemplo de uso: Incluido en index.html.
*/

// Estado global de la sesión
let usuarioActual = null;
let jugadaId = null; // Último ID procesado
let seleccionesUsuario = [];
let jugadasPendientes = []; // Carrito de jugadas
let currentFechaId = null;


document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.querySelector('.container');
    if (mainContainer) mainContainer.classList.add('oculto');

    // Actualizar fecha en el panel
    actualizarFechaReloj();

    // Verificar sesión guardada en sessionStorage
    const sesion = sessionStorage.getItem('sabes_usuario');
    if (sesion) {
        usuarioActual = JSON.parse(sesion);
        entrarAlJuego(usuarioActual);
    }
});

function actualizarFechaReloj() {
    const el = document.getElementById('fecha-actual-panel');
    if (!el) return;

    const ahora = new Date();
    const opciones = { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };
    let fechaStr = ahora.toLocaleDateString('es-AR', opciones);

    // Capitalizar primera letra
    fechaStr = fechaStr.charAt(0).toUpperCase() + fechaStr.slice(1);

    el.textContent = fechaStr;
}

// ============================================================
// TABS Login / Registro
// ============================================================
function mostrarTab(tab) {
    const formLogin = document.getElementById('form-login');
    const formRegistro = document.getElementById('form-registro');
    const tabLogin = document.getElementById('tab-login');
    const tabRegistro = document.getElementById('tab-registro');

    if (tab === 'login') {
        formLogin.style.display = 'flex';
        formRegistro.style.display = 'none';
        tabLogin.classList.add('active');
        tabRegistro.classList.remove('active');
    } else {
        formLogin.style.display = 'none';
        formRegistro.style.display = 'flex';
        tabLogin.classList.remove('active');
        tabRegistro.classList.add('active');
    }
}

// ============================================================
// LOGIN
// ============================================================
async function handleLogin(event) {
    event.preventDefault();
    const dni = document.getElementById('login-dni').value.trim();
    const password = document.getElementById('login-pass').value;
    const errorEl = document.getElementById('login-error');

    errorEl.textContent = '⏳ Conectando...';

    const { ok, data, error } = await apiLogin(dni, password);

    if (ok) {
        errorEl.textContent = '';
        usuarioActual = data.usuario;
        sessionStorage.setItem('sabes_usuario', JSON.stringify(usuarioActual));
        entrarAlJuego(usuarioActual);
    } else {
        errorEl.textContent = `❌ ${error}`;
    }
}

// ============================================================
// REGISTRO
// ============================================================
async function handleRegistro(event) {
    event.preventDefault();
    const errorEl = document.getElementById('reg-error');

    const formData = new FormData();
    formData.append('dni', document.getElementById('reg-dni').value.trim());
    formData.append('telefono', document.getElementById('reg-tel').value.trim());
    formData.append('email', document.getElementById('reg-email').value.trim());
    formData.append('fecha_nac', document.getElementById('reg-nacimiento').value);
    formData.append('direccion', document.getElementById('reg-dir').value.trim());
    formData.append('nombre', document.getElementById('reg-nombre').value.trim());
    formData.append('password', document.getElementById('reg-pass').value);

    // Archivos
    const dniFrente = document.getElementById('reg-dni-frente').files[0];
    const dniDorso = document.getElementById('reg-dni-dorso').files[0];
    const selfie = document.getElementById('reg-selfie').files[0];
    if (dniFrente) formData.append('foto_dni_frente', dniFrente);
    if (dniDorso) formData.append('foto_dni_dorso', dniDorso);
    if (selfie) formData.append('foto_selfie', selfie);

    errorEl.textContent = '⏳ Registrando...';

    const { ok, data, error } = await apiRegister(formData);

    if (ok) {
        errorEl.textContent = '';
        usuarioActual = data.usuario;
        sessionStorage.setItem('sabes_usuario', JSON.stringify(usuarioActual));
        entrarAlJuego(usuarioActual);
    } else {
        errorEl.textContent = `❌ ${error}`;
    }
}

// ============================================================
// ENTRAR AL JUEGO
// ============================================================
async function entrarAlJuego(usuario) {
    const pantallaLogin = document.getElementById('pantalla-login');
    const mainContainer = document.querySelector('.container');

    if (pantallaLogin) pantallaLogin.classList.add('oculto');
    if (mainContainer) mainContainer.classList.remove('oculto');

    // Actualizar datos del carnet de socio
    const elDni = document.getElementById('socio-dni');
    const elNombre = document.getElementById('socio-direccion');
    const elPais = document.getElementById('socio-pais');
    const elFoto = document.getElementById('foto-jugador');

    if (elDni) elDni.textContent = usuario.dni;
    if (elNombre) elNombre.textContent = usuario.nombre || usuario.direccion;
    if (elPais) elPais.textContent = "Argentina";

    // Si tiene foto (selfie), la mostramos
    if (elFoto && usuario.foto_selfie) {
        const host = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://127.0.0.1:5000'
            : ''; // En PA la ruta es relativa
        elFoto.src = `${host}/${usuario.foto_selfie}`;
        elFoto.style.display = 'block';
    }

    // Cargar los partidos desde el backend
    await cargarPartidos();
    await actualizarFichasUI();

    // Agregar botón de cerrar sesión
    agregarBotonCerrarSesion();

    // Cargar historial
    mostrarHistorial();
}

async function actualizarFichasUI() {
    if (!usuarioActual) return;
    const { ok, data } = await apiGetFichas(usuarioActual.dni);
    if (ok) {
        usuarioActual.fichas = data.fichas;
        const elFichas = document.getElementById('user-fichas');
        if (elFichas) elFichas.textContent = data.fichas;
    }
    const elPendientes = document.getElementById('pendientes-count');
    if (elPendientes) elPendientes.textContent = jugadasPendientes.length;
}

// ============================================================
// CARGAR PARTIDOS DESDE EL BACKEND
// ============================================================
async function cargarPartidos() {
    const { ok, data } = await apiGetPartidos();
    if (!ok) {
        console.warn('No se pudo obtener partidos del servidor. Usando lista local.');
        renderPartidosLocales();
        return;
    }

    const partidos = data.partidos;
    currentFechaId = data.fecha_id;

    // Actualizar Nro de Fecha en el UI
    const nroFechaEl = document.getElementById('nro-fecha');
    if (nroFechaEl) nroFechaEl.textContent = data.nro_fecha;

    // Actualizar Banner (Ticker) con los partidos reales
    actualizarTicker(partidos);

    renderPartidos(partidos, data.sorteado);
    renderPremios(partidos.length);
}

function actualizarTicker(partidos) {
    const tickerEl = document.querySelector('.ticker-text');
    if (tickerEl && partidos.length > 0) {
        const textoTicker = partidos.map(p => `${p.nombre.toUpperCase()} 0-0`).join(' | ');
        tickerEl.textContent = textoTicker + ' | ' + textoTicker;
    }
}

function renderPartidos(partidos, yasorteado = false, esOffline = false) {
    const container = document.getElementById('filas-boleta');
    if (!container) return;
    container.innerHTML = '';

    // Si no estamos conectados, agregamos una clase para poner las letras violetas
    if (esOffline) {
        container.classList.add('modo-offline');
    } else {
        container.classList.remove('modo-offline');
    }

    // Solo inicializamos si la cantidad de partidos cambió o si está vacío
    if (!seleccionesUsuario || seleccionesUsuario.length !== partidos.length) {
        seleccionesUsuario = new Array(partidos.length).fill(null);
    }

    partidos.forEach((partido, index) => {
        const row = document.createElement('div');
        row.className = 'row';

        const resultado = partido.resultado;
        const seleccionado = seleccionesUsuario[index];

        row.innerHTML = `
            <span class="partido">${index + 1}. ${partido.nombre}</span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="L" class="input-radio" ${yasorteado ? 'disabled' : ''}
                ${resultado === 'L' ? 'style="accent-color:var(--color-acento)"' : ''}></span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="E" class="input-radio" ${yasorteado ? 'disabled' : ''}
                ${resultado === 'E' ? 'style="accent-color:var(--color-acento)"' : ''}></span>
            <span class="opcion"><input type="radio" name="partido_${index}" value="V" class="input-radio" ${yasorteado ? 'disabled' : ''}
                ${resultado === 'V' ? 'style="accent-color:var(--color-acento)"' : ''}></span>
        `;

        // Guardar selección al hacer click
        row.querySelectorAll('input[type="radio"]').forEach(input => {
            input.addEventListener('change', () => {
                seleccionesUsuario[index] = input.value;
            });
        });

        container.appendChild(row);
    });
}

function renderPremios(count) {
    const container = document.getElementById('premios-dinamicos');
    if (!container) return;
    container.innerHTML = '';

    // Lógica de premios: 
    // Todos, count-1, count-2, count-3
    const montos = [500000, 50000, 10000, 5000];
    const labels = [
        `${count} Aciertos`,
        `${count - 1} Aciertos`,
        `${count - 2} Aciertos`,
        `${count - 3} Aciertos`
    ];

    labels.forEach((label, i) => {
        const li = document.createElement('li');
        li.className = 'premio-item';
        li.innerHTML = `
            <span>${label}</span>
            <span class="${i === 0 ? 'dorado' : ''}">$${montos[i].toLocaleString()}</span>
        `;
        container.appendChild(li);
    });
}

function renderPartidosLocales() {
    // Fallback con partidos de la Fecha 9 si el backend no responde
    const partidos = [
        { nombre: "Gimnasia (Mza.) vs Defensa y Justicia", resultado: null },
        { nombre: "Barracas Central vs Banfield", resultado: null },
        { nombre: "Platense vs Estudiantes", resultado: null },
        { nombre: "Vélez Sársfield vs Newell’s", resultado: null },
        { nombre: "Unión vs Talleres", resultado: null },
        { nombre: "Rosario Central vs Tigre", resultado: null },
        { nombre: "Aldosivi vs Independiente Rivadavia Mza.", resultado: null },
        { nombre: "Estudiantes (Río Cuarto) vs Instituto", resultado: null },
        { nombre: "San Lorenzo vs Independiente", resultado: null },
        { nombre: "Racing vs Huracán", resultado: null },
        { nombre: "Belgrano vs Sarmiento", resultado: null },
        { nombre: "Central Córdoba vs Boca", resultado: null },
        { nombre: "River vs Atlético Tucumán", resultado: null },
    ];
    // Actualizar Banner (Ticker) incluso en modo local/offline
    actualizarTicker(partidos);

    // Pasamos 'true' como tercer parámetro para activar el modo offline (violeta)
    renderPartidos(partidos, false, true);
}

// ============================================================
// BOTONES DE JUEGO (CARRITO Y FICHAS)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const btnOtra = document.getElementById('btn-otra-jugada');
    const btnConfirmar = document.getElementById('btn-confirmar-boleta');

    if (btnOtra) {
        btnOtra.addEventListener('click', () => {
            const vacias = seleccionesUsuario.filter(s => !s).length;
            if (vacias > 0) {
                alert(`Completá todos los partidos para acumular otra jugada. Faltan ${vacias}.`);
                return;
            }
            // Guardar copia de la jugada actual en pendientes
            jugadasPendientes.push([...seleccionesUsuario]);

            // Limpiar UI para la siguiente jugada
            document.querySelectorAll('.input-radio').forEach(rb => rb.checked = false);
            seleccionesUsuario.fill(null);

            actualizarFichasUI();
            alert("✅ Jugada agregada al carrito. ¡Podés hacer otra!");
        });
    }

    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', async () => {
            if (!usuarioActual) {
                alert('Debés iniciar sesión primero.');
                return;
            }

            // Forzar que la boleta actual esté completa para poder jugar
            const actualesCompletas = seleccionesUsuario.filter(s => s).length === seleccionesUsuario.length;

            if (!actualesCompletas) {
                const faltantes = seleccionesUsuario.filter(s => !s).length;
                alert(`❌ Boleta incompleta. Completá los ${faltantes} partidos restantes de la boleta actual.`);
                return;
            }

            let jugadasAEnviar = [...jugadasPendientes];
            jugadasAEnviar.push([...seleccionesUsuario]);

            const costo = jugadasAEnviar.length;
            if (usuarioActual.fichas < costo) {
                alert(`❌ Fichas insuficientes. Necesitás ${costo} fichas y tenés ${usuarioActual.fichas}.`);
                return;
            }

            btnConfirmar.disabled = true;
            btnConfirmar.innerText = 'PROCESANDO...';

            // Guardar jugadas masivamente
            const res = await apiGuardarJugadas(usuarioActual.dni, jugadasAEnviar);

            // 3. Procesar respuesta
            if (res.ok) {
                actualizarFichasUI();
                jugadasPendientes = [];
                actualizarListaPendientes();
                alert(`¡Éxito! Se procesaron ${res.data.jugadas_ids.length} jugadas.`);

                // DESCARGA MÚLTIPLE DE TICKETS
                // El backend devuelve jugadas_ids. Para descargar con detalle, necesitaremos
                // que el ticket visual se actualice por cada una.
                // Como ya tenemos 'jugadasParaEnviar', podemos iterar sobre ellas.
                for (let i = 0; i < res.data.jugadas_ids.length; i++) {
                    const idJugada = res.data.jugadas_ids[i];
                    const itemNum = i + 1;
                    const jugadaData = {
                        dni: usuarioActual.dni,
                        partidos: partidosActuales.map((p, idx) => ({
                            nombre: `${p.equipo_local} vs ${p.equipo_visitante}`,
                            seleccion: jugadasParaEnviar[i].selecciones[idx]
                        }))
                    };

                    renderTicketVisual(idJugada, jugadaData);
                    await descargarTicketPersonalizado(usuarioActual.dni, idJugada, itemNum);
                }

                jugadaId = res.data.jugadas_ids[0];
                btnConfirmar.innerText = 'SORTEANDO...';
                lanzarAnimacionRuleta();
            } else {
                alert(`Error al guardar: ${res.error}`);
                btnConfirmar.disabled = false;
                btnConfirmar.innerText = 'JUEGA BOLETA';
            }
        });
    }

    const btnHist = document.getElementById('btn-historial');
    if (btnHist) btnHist.addEventListener('click', mostrarHistorial);

    const btnComprar = document.getElementById('btn-comprar-fichas');
    if (btnComprar) {
        btnComprar.addEventListener('click', async () => {
            if (!usuarioActual) {
                alert("Iniciá sesión para comprar fichas.");
                return;
            }
            const res = await apiComprarFichas(usuarioActual.dni);
            if (res.ok) {
                alert(res.data.message);
                actualizarFichasUI();
            } else {
                alert(`Error en la compra: ${res.error}`);
            }
        });
    }
});

function lanzarAnimacionRuleta() {
    const ruletaSlot = document.getElementById('slot-1');
    const resultadosPosibles = ['L', 'E', 'V'];
    let counter = 0;
    const spinInterval = setInterval(() => {
        if (ruletaSlot) {
            ruletaSlot.innerText = resultadosPosibles[Math.floor(Math.random() * 3)];
        }
        counter++;
        if (counter > 20) {
            clearInterval(spinInterval);
            ejecutarSorteo();
        }
    }, 100);
}

// ============================================================
// EJECUTAR SORTEO EN EL BACKEND
// ============================================================
async function ejecutarSorteo() {
    const { ok, data, error } = await apiSortear(jugadaId);

    if (!ok) {
        console.error('Error en sorteo:', error);
        return;
    }

    // Actualizar UI con resultados reales
    renderPartidos(data.partidos, true);

    const ruletaSlot = document.getElementById('slot-1');
    if (ruletaSlot && data.resultados?.length) {
        ruletaSlot.innerText = data.resultados[0]; // Mostrar primer resultado
    }

    const aciertos = data.aciertos ?? 0;
    mostrarResultado(aciertos);

    // Mostrar el Ticket (Comprobante)
    mostrarTicket(data.jugada_id, data.partidos);

    // Permitir volver a jugar después de un breve delay
    const btnConfirmar = document.getElementById('btn-confirmar-boleta');
    setTimeout(() => {
        if (btnConfirmar) {
            btnConfirmar.innerText = 'JUEGA BOLETA';
            btnConfirmar.disabled = false;
        }
    }, 5000);
}

function renderTicketVisual(id, partidos) {
    document.getElementById('t-dni').textContent = usuarioActual.dni;
    document.getElementById('ticket-id').textContent = `JUGADA #${String(id).padStart(5, '0')}`;
    document.getElementById('t-timestamp').textContent = new Date().toLocaleString();

    const lista = document.getElementById('ticket-lista-partidos');
    lista.innerHTML = partidos.map((p, i) => `
        <p>
            <span>${i + 1}. ${p.nombre}</span> 
            <b>${p.seleccion}</b>
        </p>`).join('');
}

function mostrarTicket(id, partidos) {
    renderTicketVisual(id, partidos);
    document.getElementById('container-ticket').classList.remove('oculto');
    document.getElementById('container-ticket').scrollIntoView({ behavior: 'smooth' });
}

async function descargarTicketPersonalizado(dni, jugadaId, item) {
    const area = document.getElementById('ticket-capture-area');
    const nroFecha = document.getElementById('t-fecha').textContent || "9";
    const filename = `${dni}_${jugadaId}_${item}.png`;

    try {
        const canvas = await html2canvas(area, {
            backgroundColor: '#fdf5e6',
            scale: 2,
            useCORS: true,
            logging: false
        });

        const link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL("image/png");
        link.click();
        // Delay para evitar bloqueos de descargas masivas en navegadores
        await new Promise(r => setTimeout(r, 600));
    } catch (err) {
        console.error("Error capturando ticket:", err);
    }
}

function cerrarTicket() {
    document.getElementById('container-ticket').classList.add('oculto');
    const btnJugar = document.querySelector('.btn-jugar');
    if (btnJugar) {
        btnJugar.innerText = 'JUGAR NUEVA BOLETA';
        btnJugar.disabled = false;
    }
}

async function descargarTicket() {
    const area = document.getElementById('ticket-capture-area');
    const dni = usuarioActual.dni;
    const nroFecha = document.getElementById('t-fecha').textContent || "9";
    const filename = `${dni}_${nroFecha}.png`;

    try {
        // html2canvas para capturar el área del ticket como imagen
        const canvas = await html2canvas(area, {
            backgroundColor: '#fdf5e6',
            scale: 2,
            useCORS: true,
            logging: false
        });

        const link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL("image/png");
        link.click();
    } catch (err) {
        console.error("Error capturando ticket:", err);
        alert("Error al generar la imagen. Intentá de nuevo.");
    }
}

// ============================================================
// MOSTRAR RESULTADO FINAL
// ============================================================
function mostrarResultado(aciertos) {
    const premioMayor = document.querySelector('.premio-mayor');

    let mensaje = `🎯 ${aciertos} aciertos`;
    if (aciertos === 13) {
        mensaje = `🏆 ¡13 ACIERTOS! ¡GANASTE EL POZO!`;
        if (premioMayor) premioMayor.classList.add('glow');
        triggerSuccessAnimation();
    } else if (aciertos >= 10) {
        mensaje += ' — ¡Premio!';
        triggerSuccessAnimation();
    } else {
        mensaje += ' — ¡Mejor suerte la próxima!';
        triggerFailAnimation();
    }

    // Mostrar en pantalla
    const ticker = document.querySelector('.ticker-text');
    if (ticker) {
        ticker.textContent = ` ${mensaje} | `;
    }

    alert(mensaje);
}

// ============================================================
// HISTORIAL
// ============================================================
async function mostrarHistorial() {
    if (!usuarioActual) return;
    const { ok, data } = await apiHistorial(usuarioActual.dni);
    if (!ok) { alert('No se pudo obtener el historial.'); return; }

    const jugadas = data.historial;
    const container = document.getElementById('historial-ticket-style');
    if (!container) return;

    if (!jugadas.length) {
        container.innerHTML = '<p class="no-jugadas">No tenés jugadas registradas aún.</p>';
    } else {
        const html = jugadas.sort((a, b) => b.id - a.id).map(j => `
            <div class="ticket-historial card-retro">
                <div class="ticket-header-sm">
                    <span>JUGADA #${String(j.id).padStart(5, '0')}</span>
                    <span class="fecha-sm">${j.fecha || ''}</span>
                </div>
                <div class="ticket-body-sm">
                    <span class="aciertos-sm">${j.aciertos ?? 0} ACIERTOS</span>
                </div>
            </div>
        `).join('');
        container.innerHTML = html;
        container.scrollIntoView({ behavior: 'smooth' });
    }
}

function cerrarHistorial() {
    document.getElementById('modal-historial').classList.add('oculto');
}

// ============================================================
// CERRAR SESIÓN
// ============================================================
function agregarBotonCerrarSesion() {
    const perfilSection = document.querySelector('.perfil-jugador');
    if (!perfilSection || document.getElementById('btn-cerrar-sesion')) return;

    const btn = document.createElement('button');
    btn.id = 'btn-cerrar-sesion';
    btn.textContent = 'Cerrar Sesión';
    btn.style.cssText = 'margin-top:8px;padding:6px 14px;font-family:Courier New;font-size:12px;background:#922b21;color:white;border:none;cursor:pointer;border-radius:4px;';
    btn.addEventListener('click', () => {
        sessionStorage.removeItem('sabes_usuario');
        usuarioActual = null;
        location.reload();
    });
    perfilSection.appendChild(btn);
}

// ============================================================
// ANIMACIONES de victoria / derrota (sin cambios)
// ============================================================
function triggerSuccessAnimation() {
    for (let i = 0; i < 50; i++) {
        const confeti = document.createElement('div');
        confeti.classList.add('confeti');
        confeti.classList.add(Math.random() > 0.5 ? 'blanco' : 'celeste');
        confeti.style.left = Math.random() * 100 + 'vw';
        confeti.style.animationDuration = (Math.random() * 3 + 2) + 's';
        confeti.style.opacity = Math.random();
        document.body.appendChild(confeti);
        setTimeout(() => confeti.remove(), 5000);
    }
}

function triggerFailAnimation() {
    const boleta = document.querySelector('.boleta-digital');
    if (boleta) {
        boleta.classList.add('derrota-anim');
        setTimeout(() => boleta.classList.remove('derrota-anim'), 2000);
    }
}
