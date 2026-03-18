# Charla 02 — Integración de MercadoPago, Fichas Libres y Refactorización de Base de Datos
**Fecha:** 12 de marzo de 2026

---

## 1. Fichas por Cantidad Libre (Reemplazo de Paquetes)

Se modificó la lógica comercial y de UI para abandonar el sistema de "paquetes pre-armados". Ahora se permite al socio ingresar una cantidad libre de fichas a adquirir.
- **Regla de Negocio:** Se requieren **2500 fichas** para jugar un ticket de boleta completo, y en Argentina el valor es **1 ficha = $1 ARS**.
- **Cambios en UI:** El componente `frontend/src/components/CompraFichasModal.jsx` se rediseñó bajo estética retro, sugiriendo el monto faltante al operador mediante un input numérico que precalcula inteligentemente: `max(2500 - fichas_actuales, 1)`.
- **Backend Adaptado:** `backend/services.py` pasó a recibir montos dinámicos en vez de *strings* de paquetes. El registro en la base de datos impacta como `libre_{cantidad}`.

---

## 2. Corrección Crítica de Base de Datos (`cantidad_fichas` → `fichas`)

El sistema fallaba al intentar grabar en MercadoPago por una inconsistencia de esquema en la base de datos (se esperaba `fichas`, pero la columna física real era `cantidad_fichas` bajo una restricción de `NOT NULL`).
- **Script Local:** Se generó `backend/fix_columna_fichas.py` capaz de leer `sabes_de_futbol.db` y realizar un `DROP` + `CREATE` controlado preservando los datos integrales de los usuarios mediante relaciones foráneas sanas.
- **Entorno Productivo Inteligente:** Para evitar lidiar con repositorios bloqueados en el hosting, en `backend/app.py` se sumó el endpoint `/api/admin/migrar-pagos-fichas`, permitiendo lanzar la reparación SQLite de forma remota en **PythonAnywhere** usando seguridad vía encabezado `X-Admin-Secret`.

---

## 3. Manejo de Retorno de Checkout y Polling Automático

Previamente, tras abonar por MercadoPago, el cliente regresaba a la pantalla sin ningún tipo de feedback.
- **Interceptación Visual (`useEffect`):** El layout principal de React en `frontend/src/App.jsx` ahora intercepta automáticamente el regreso en la URL (`?pago=success` o `failure`). 
- **Banner Retro:** Dependiendo de la variable obtenida de MP, inyecta por pantalla notificaciones personalizadas verdes, rojas o amarillas configuradas en `index.css` (`.banner-pago`).
- **Polling de Acreditación:** Al detectar un `success`, puede haber una latencia o un _race condition_ entre el cliente volviendo y el _webhook_. Por eso, se creó un mecanismo (polling a `/api/usuario/estado-ultimo-pago`) que consulta la base de datos recursivamente cada pocos segundos hasta observar que el saldo se impactó y recargar las _"Fichas en balance"_ sin fricciones.

---

## 4. Detalle de Experiencia de Usuario: Rango de Fechas del Fixture

Además de la pasarela, se inyectó una mejora visual clave en el front.
- **Rango Inteligente:** En `frontend/src/components/PanelFixture.jsx`, el sistema ahora calcula dinámicamente qué días interviene la fecha en curso basándose en la configuración enviada desde el administrador (ejemplo: `DOM 10/03 → LUN 11/03`), otorgando un norte mental mucho más profesional para el apostador en la cabecera.

---

## 5. Migración de BD en Producción (PythonAnywhere sin Git)

El entorno de producción en PythonAnywhere no tiene repositorio Git configurado. Los archivos se actualizan manualmente vía panel Files o consola Bash con `curl`.
- **Problema:** El script `fix_columna_fichas.py` buscaba `sabes.db` pero la BD real se llama `sabes_de_futbol.db` en `backend/`. Se corrigieron las rutas.
- **Solución directa:** Se ejecutó la recreación de la tabla `pagos_fichas` directamente desde la consola Bash de PythonAnywhere con un script Python inline, sin tocar archivos.
- **Flujo de actualización en producción:** `curl -o ~/sabes_de_futbol/backend/app.py "https://raw.githubusercontent.com/oaf2023/sabes_de_futbol/main/backend/app.py"` + Reload en panel Web.

---

## 6. Credenciales de MercadoPago — Decisión de Entorno

Se analizaron en detalle las tres opciones de credenciales disponibles:
- **Token TEST- de cuenta real:** Crea preferencias en modo sandbox pero el comprador también debe ser usuario de prueba. No se puede mezclar con usuarios/tarjetas reales.
- **Token TEST- de vendedor001:** Requiere iniciar sesión con el usuario de prueba `TESTUSER2996047549092111920` en el panel de MP para obtenerlo. Los usuarios de prueba no tienen email real — el código de verificación de MP se obtiene desde el panel de desarrolladores → Cuentas de prueba.
- **Token APP_USR- (producción):** Acepta cualquier tarjeta real. Dinero llega directamente a la cuenta del titular.

**Decisión adoptada:** Se activó el token de **producción** `APP_USR-1281009980698993-...` en `MERCADOPAGO_ACCESS_TOKEN`. Los pagos son reales desde este momento. El token TEST- queda documentado en `.env` como `acces_token_prueba` para referencia futura.

**Pendiente:** Crear una aplicación propia en el panel de MP con el nombre "Sabes de Fútbol" para que aparezca ese nombre en el checkout en lugar del nombre personal del titular de la cuenta.

---

## Charla 03 — Logo, Zona Horaria Argentina, Bugs de Jugada y Acreditación de Fichas

**Fecha:** 13 de marzo de 2026

---

## 1. Logo en toda la aplicación

Se incorporó el archivo `logo_sabesdefutbol.png` (ubicado en la raíz del proyecto) en todos los puntos de contacto visual.
- **Login (`AuthScreen.jsx`):** Se reemplazó el texto `SABES DE FUTBOL` por la imagen del logo centrada con separador punteado. Se agrega `CARNET DE SOCIO` como subtítulo.
- **Header fijo (`App.jsx`):** Se agregó un `<header className="app-header">` fijo en la parte superior, visible en toda la app luego de loguearse. Muestra el logo a la izquierda y **fecha + hora en tiempo real** (actualización cada segundo) a la derecha.
- **Ticket de jugada (`TicketModal.jsx`):** El título textual fue reemplazado por el logo. Compatible con la descarga PNG vía `html2canvas` (`useCORS: true`).
- **Modal de compra de fichas (`CompraFichasModal.jsx`):** Logo agregado arriba del título "COMPRAR FICHAS" con separador punteado.
- **Despliegue en producción:** El logo se sirve desde `frontend/public/logo.png` → Vite lo copia a `frontend/dist/logo.png` al hacer `npm run build`. En PythonAnywhere: hacer build primero y luego copiar manualmente el logo a `dist/`.

---

## 2. Zona Horaria Argentina (UTC-3) en todo el sistema

El sistema usaba `datetime.utcnow()` en el backend, lo que causaba que las comparaciones de horario (¿ya comenzó la fecha?) estuvieran desfasadas 3 horas.

**Estrategia adoptada:** La DB sigue almacenando en UTC (práctica estándar), pero todas las comparaciones de negocio y los timestamps de resolución usan hora Argentina.

- **`backend/services.py`:** Se agregó `AR_TZ = timezone(timedelta(hours=-3))` y la función `ahora_ar()`. Todos los `datetime.utcnow()` en lógica de negocio fueron reemplazados.
- **`backend/app.py`:** Ídem con función local `ahora_ar()`. La comparación `fecha_comenzada` en `/api/partidos` ahora usa hora Argentina.
- **Frontend — reloj del header:** `toLocaleTimeString` forzado con `timeZone: 'America/Argentina/Buenos_Aires'`, independiente de la zona del dispositivo del usuario.
- **Frontend — fechas al usuario:** Se creó `frontend/src/utils/fechaAR.js` con la función `fechaAR(isoString, conHora)` que convierte cualquier ISO UTC del backend a string legible en zona Argentina. Aplicada en `TicketModal.jsx` y `PerfilHistorico.jsx`.

---

## 3. Bug: No dejaba jugar la Fecha 11 con la Fecha 10 activa y ya comenzada

**Causa:** `GameService.guardar_jugadas()` siempre tomaba la `FechaActual` activa y bloqueaba si ya había comenzado, sin importar si la jugada era para la próxima fecha.

**Solución:**

- `guardar_jugadas()` en `services.py` ahora acepta un parámetro opcional `fecha_sorteo_id`. Si viene, usa esa fecha directamente y solo valida que no haya comenzado ella misma.
- El endpoint `/api/jugada` en `app.py` lee y pasa el campo `fecha_sorteo_id` del body.
- `handleJugarBoletasProxima` en `App.jsx` ahora incluye `fecha_sorteo_id: proximaFecha.fecha_id` en el body del POST.

---

## 4. Bug: Fichas no se actualizaban tras el pago

**Causa raíz (doble):**

1. El polling consultaba `/api/usuario/estado-ultimo-pago` (el último pago del usuario), que podía ya estar `aprobado` de una compra anterior, disparando un falso positivo inmediatamente.
2. `actualizarFichas()` actualizaba el estado React pero no el `sessionStorage`, por lo que si el usuario recargaba la página, el contador volvía al valor anterior.

**Solución:**

- El endpoint `/api/iniciar-pago` ahora devuelve `pago_id` (el ID del registro recién creado en `pagos_fichas`).
- Se agregó el endpoint `GET /api/usuario/pago/<pago_id>` que retorna el estado de un pago específico, verificando que pertenezca al usuario autenticado.
- El polling en `App.jsx` usa `/api/usuario/pago/{pagoId}` cuando dispone del ID, eliminando los falsos positivos.
- `actualizarFichas()` ahora sincroniza también `sessionStorage` con el nuevo saldo.

---

## 5. Panel Admin: Error HTTP 403

**Causa:** El `ADMIN_SECRET` en `backend/.env` local tenía el valor placeholder `cambiar-admin-secret-en-produccion`, mientras que `admin/.env` enviaba `estaes2026laclaveapi`.

**Solución local:** Se sincronizó `backend/.env` con `ADMIN_SECRET=estaes2026laclaveapi`.

**Acción requerida en PythonAnywhere:** Editar `backend/.env` en producción y setear el mismo valor, luego Reload de la web app.
