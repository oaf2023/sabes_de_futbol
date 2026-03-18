# Charla 01 — Sabes de Fútbol
**Fecha:** 11 de marzo de 2026

---

## 1. Rediseño del Carnet de Socio

Se modificó el componente `frontend/src/components/PerfilJugador.jsx` para que el carnet de socio tenga la apariencia de la imagen de referencia:

- Título **CARNET DE SOCIO** en azul cursiva negrita
- Botón **"Mi Cuenta"** en rojo, esquina superior derecha del header
- Foto del socio a la izquierda con marco blanco
- Datos: Socio (DNI), Nombre, País
- Dos botones: **MIS JUGADAS (HISTORIAL)** (azul, más grande) y **CERRAR SESIÓN** (rojo, más pequeño)
- Banner inferior: **✓ DATOS COMPLETOS** (verde) o **⚠ DATOS INCOMPLETOS** (naranja)

**Archivos modificados:**
- `frontend/src/components/PerfilJugador.jsx`
- `frontend/src/index.css`

---

## 2. Corrección de Warning CSS

Se encontró un bloque CSS sin cerrar en `frontend/src/index.css`:

```css
/* ANTES (roto) */
.estado-cuenta {
    margin-top: 10px;
    padding: 5px;
/* comentario sin cerrar la llave */

/* DESPUÉS (corregido) */
.estado-cuenta {
    margin-top: 10px;
    padding: 5px;
}
```

---

## 3. Botón "Mi Cuenta"

Se agregó el botón **Mi Cuenta** en la esquina superior derecha del carnet. Al hacer click abre el modal `MiCuentaModal` que:

- Pide la contraseña para verificar identidad
- Permite editar: nombre, teléfono, dirección, fecha de nacimiento, email y fotos
- **No permite** modificar DNI ni contraseña
- El backend recalcula automáticamente `completado = 'SI'` si todos los campos están completos

---

## 4. Corrección de Pantalla en Blanco (Error MIME)

**Problema:** El browser pedía `/src/main.jsx` en vez del bundle compilado, causando error:
```
Failed to load module script: Expected a JavaScript-or-Wasm module script
but the server responded with a MIME type of "text/html"
```

**Causa:** `vite.config.js` tenía `base: './'` que generaba rutas relativas `./assets/...`

**Solución:**
- Cambiar `base: './'` → `base: '/'` en `frontend/vite.config.js`
- Corregir `backend/app.py` para que la función `serve()` no intercepte rutas `/api/` ni `/uploads/`

---

## 5. Análisis de Seguridad

Se identificaron **18 vulnerabilidades** en la aplicación:

### Críticas (4)
1. **Debug mode activo** — `app.run(debug=True)` expone el debugger interactivo
2. **Secretos en git** — `.env` con JWT_SECRET_KEY y token de MercadoPago versionado
3. **Sin autenticación en endpoints** — `/api/historial/<dni>`, `/api/usuario/<dni>/fichas`, `/api/jugada/<id>` accesibles por cualquiera
4. **DNI del cliente sin verificar** — Se aceptaba el DNI del body sin validar que pertenece al usuario

### Altas (8)
- CORS abierto a todos los orígenes
- Sin rate limiting (fuerza bruta posible)
- Webhook de MercadoPago sin verificar firma
- Upload de fotos solo valida extensión, no contenido real
- Enumeración de jugadas por ID incremental
- Actualización de datos sin verificar propiedad
- DNI enviado a webhook externo
- Sin validación de input en servidor

### Medias (4)
- Datos sensibles en `sessionStorage`
- `to_dict()` devuelve todos los datos personales
- HTTPS no forzado
- Dependencias sin versiones exactas

---

## 6. Implementación de Seguridad para Producción

### Archivos nuevos creados:
- `backend/auth.py` — Módulo JWT con `create_jwt_token`, `verify_jwt_token`, decorador `@require_auth`
- `frontend/src/utils/fetchWithAuth.js` — Wrapper de fetch que agrega JWT automáticamente
- `.gitignore` — Protege `.env`, `*.db`, uploads, node_modules, etc.

### Archivos modificados:

**`backend/app.py`**
- Login devuelve `{ usuario, token }` con JWT de 7 días
- Decorador `@require_auth` aplicado a todos los endpoints protegidos
- Cada endpoint valida que el usuario solo acceda a sus propios datos (403 si intenta acceder a datos ajenos)
- CORS restringido a `https://www.sabesdefutbol.com` y `localhost:5173`
- Rate limiting: 5 intentos/minuto en login y verificar-password
- `debug=False`
- Validación de firma HMAC en webhook de MercadoPago
- Validación de magic bytes en archivos subidos (no solo extensión)
- DNI sanitizado (solo dígitos)

**`backend/requirements.txt`**
```
Flask-Limiter==3.5.0   (agregado)
PyJWT==2.8.0           (agregado)
requests==2.31.0       (versión fijada)
python-dotenv==1.0.0   (versión fijada)
```

**`frontend/src/App.jsx`**
- Guarda JWT en `sessionStorage` al hacer login
- Limpia JWT al hacer logout
- Reemplaza todos los `fetch()` por `fetchWithAuth()`
- Elimina `dni` del body en requests protegidos

**`frontend/src/components/AuthScreen.jsx`**
- Pasa el token al callback `onLogin(usuario, token)`

**`frontend/src/components/PerfilHistorico.jsx`**
- Usa `fetchWithAuth` para cargar el historial

**`frontend/src/components/MiCuentaModal.jsx`**
- Usa `fetchWithAuth` en verificar-password y actualizar
- No envía DNI en el body (el backend lo obtiene del JWT)

---

## 7. Cómo actualizar PythonAnywhere

### Archivos a subir:
| Archivo local | Destino en PythonAnywhere |
|---|---|
| `backend/app.py` | `~/sabes_de_futbol/backend/app.py` |
| `backend/auth.py` | `~/sabes_de_futbol/backend/auth.py` |
| `backend/requirements.txt` | `~/sabes_de_futbol/backend/requirements.txt` |
| `frontend/dist/index.html` | `~/sabes_de_futbol/frontend/dist/index.html` |
| `frontend/dist/assets/index-BVVhPRYv.js` | `~/sabes_de_futbol/frontend/dist/assets/` (borrar el .js viejo) |
| `.gitignore` | `~/sabes_de_futbol/.gitignore` |

### Comandos en consola Bash de PythonAnywhere:
```bash
# Instalar nuevas dependencias
pip install PyJWT==2.8.0 Flask-Limiter==3.5.0

# Generar clave JWT segura
python3 -c "import secrets; print(secrets.token_hex(32))"

# Editar el .env con la nueva clave
nano ~/sabes_de_futbol/backend/.env
# Cambiar: JWT_SECRET_KEY=<pegar la clave generada>
# Guardar: Ctrl+O → Enter → Ctrl+X
```

Luego hacer **Reload** en el panel Web.

---

## 8. Nota sobre Environment Variables en PythonAnywhere

El plan actual de PythonAnywhere **no incluye** la sección "Environment Variables" en el panel Web. La alternativa es editar el archivo `.env` directamente en el servidor via consola Bash. El `.env` ya fue removido del tracking de git (`git rm --cached backend/.env`) por lo que es seguro tenerlo solo en el servidor.

---

## 9. Corrección de Error de Conexión en Login (JWT_SECRET_KEY)

**Problema:** Al intentar ingresar, el browser mostraba "Error de conexión". La consola revelaba `500 INTERNAL SERVER ERROR` en `/api/login`.

**Causa:** `backend/auth.py` valida que `JWT_SECRET_KEY` no contenga la palabra `"cambiar"`. El `.env` local tenía el valor placeholder `cambiar-en-produccion-...`, lo que lanzaba un `RuntimeError` al intentar firmar el JWT.

**Solución:** Generar una clave real y reemplazarla en `backend/.env`:
```
JWT_SECRET_KEY=3b9dbf8d4116d15f05dc6e8007a891dd80ea947e4ea6bc83b07ab2cea5fa9442
```
En PythonAnywhere hacer lo mismo via `nano ~/sabes_de_futbol/backend/.env` y luego **Reload**.

---

## 10. Script activar_fecha.py

Se creó `backend/activar_fecha.py` para activar una fecha de jugada por país directamente desde consola:

```bash
python activar_fecha.py --fec 10 --pais 1
```

**Qué hace:**
- Busca el registro en `fecha_actual` para el `pais_id` indicado
- Si existe → actualiza `nro_fecha` (muestra el cambio anterior → nuevo)
- Si no existe → lo crea
- Verifica que el país exista (error si no)
- Muestra el estado completo de `fecha_actual` al finalizar

---

## 11. Panel Fixture (PanelFixture.jsx)

Se creó el componente `frontend/src/components/PanelFixture.jsx` que ocupa la 4ta columna del layout (recuadro rojo en el diseño). Muestra el fixture completo de la fecha activa en estilo retro, agrupado por día.

**Características:**
- Partidos **agrupados por día** (MAR 10/03, MIÉ 11/03, JUE 12/03...)
- Finalizados → marcador real `1 - 1` en badge azul/amarillo retro
- Pendientes → hora del partido (`17:30`, `19:45`)
- Barra de progreso `X/15 jugados`
- Auto-refresco cada 60 segundos

**Archivos modificados/creados:**
- `frontend/src/components/PanelFixture.jsx` — nuevo componente
- `frontend/src/App.jsx` — import y render de `<PanelFixture>`
- `frontend/src/index.css` — estilos `.fx-*`

**Cambios en backend:**
- `backend/models.py` — `Partido` ahora tiene `fecha_hora`, `goles_local`, `goles_visitante`
- `backend/app.py` — `/api/partidos` expone `local`, `visitante`, `resultado`, `goles_local`, `goles_visitante`, `fecha_hora`
- `backend/migrate_fecha_hora.py` — migración de las 3 columnas nuevas
- `backend/sync_fixtures.py` — actualizado para soportar formato enriquecido (objeto con horarios y goles)
- `backend/fixtures.json` — Fecha 10 cargada con horarios y resultados reales (Torneo Apertura 2026)

**Comandos en PythonAnywhere:**
```bash
python migrate_fecha_hora.py
python sync_fixtures.py
```

---

## 12. Panel de Administración Streamlit

Se creó `admin/admin_panel.py`, un panel de administración **totalmente independiente** que corre localmente y opera directo sobre la BD de PythonAnywhere (via SFTP/ruta local).

**Instalación:**
```bash
cd admin
pip install -r requirements.txt
streamlit run admin_panel.py
```

**Configuración:** `admin/.env`
```
DB_PATH=../backend/sabes_de_futbol.db
ADMIN_PASSWORD=tu_clave
```

**Secciones:**

| Sección | Funcionalidad |
|---|---|
| 📊 Dashboard | Métricas globales, últimos socios, últimas jugadas, fecha activa por país |
| 📅 Fechas & Fixture | Activar fecha por país, ver fixture con marcadores, crear nueva fecha |
| ⚽ Resultados | Cargar goles (local/visitante) y resultado (L/E/V) para cada partido |
| 👥 Socios | Buscar socios, editar datos, resetear contraseña |
| 🪙 Fichas | Acreditar fichas manualmente con motivo y registro en `pagos_fichas` |
| 💳 Pagos | Ver pagos pendientes de MP, aprobar/rechazar manualmente |

**Archivos creados:**
- `admin/admin_panel.py`
- `admin/.env`
- `admin/requirements.txt`

---

## 13. Admin vía API HTTP (Conexión a PythonAnywhere en tiempo real)

Se migró el panel de administración de sqlite3 local a llamadas HTTP a la API de producción. El admin ahora opera directamente sobre la DB de PythonAnywhere sin necesidad de montar SFTP ni acceder a la consola Bash.

### Arquitectura

```
admin_panel.py (local Streamlit)
    ↓ HTTP con X-Admin-Secret
https://www.sabesdefutbol.com/api/admin/*
    ↓
Flask (PythonAnywhere) → SQLAlchemy → sabes_de_futbol.db
```

### Endpoints agregados en `backend/app.py`

Todos protegidos con `require_admin` (header `X-Admin-Secret` comparado con HMAC):

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/admin/stats` | GET | Métricas globales + últimos socios + fechas activas |
| `/api/admin/paises` | GET | Lista de países |
| `/api/admin/fechas` | GET | Fechas por país |
| `/api/admin/fecha-activa` | GET | Fecha activa por país |
| `/api/admin/activar-fecha` | POST | Activa una fecha |
| `/api/admin/partidos` | GET | Partidos de una fecha |
| `/api/admin/resultado` | POST | Actualiza goles + resultado de un partido |
| `/api/admin/nueva-fecha` | POST | Crea fecha con partidos |
| `/api/admin/partido/<id>` | DELETE | Elimina un partido |
| `/api/admin/socios` | GET | Lista socios con filtro |
| `/api/admin/socio/<dni>` | GET/POST | Ver/editar socio |
| `/api/admin/acreditar-fichas` | POST | Acredita fichas manualmente |
| `/api/admin/pagos` | GET | Lista pagos con filtro de estado |
| `/api/admin/pago/<id>/aprobar` | POST | Aprueba pago y acredita fichas |
| `/api/admin/pago/<id>/rechazar` | POST | Rechaza pago |
| `/api/admin/jugadas` | GET | Últimas 50 jugadas |

### Configuración

**`admin/.env`:**
```
API_BASE=https://www.sabesdefutbol.com
ADMIN_SECRET=estaes2026laclaveapi
ADMIN_PASSWORD=admin1234
```

**`backend/.env` en PythonAnywhere** debe tener:
```
ADMIN_SECRET=estaes2026laclaveapi
```

### `admin/admin_panel.py` reescrito

- Eliminado todo `sqlite3` directo
- Funciones `api_get`, `api_post`, `api_delete` como cliente HTTP
- Sección "Ver Fixture" muestra cada partido con `#id` y botón 🗑 para eliminar duplicados

### Fix de duplicados en DB

Se detectaron partidos duplicados en fecha 10 (Newell's vs Platense aparecía dos veces). Solución:
1. Ir a **Fechas & Fixture → Ver Fixture → Fecha 10**
2. Identificar el duplicado por `#id`
3. Eliminarlo con el botón 🗑

Se creó también `backend/fix_duplicados.py` como alternativa (borra todos los partidos de fecha 10 y los recarga desde `fixtures.json`).

**Archivos modificados/creados:**
- `backend/app.py` — agregados 16 endpoints `/api/admin/*` + decorador `require_admin`
- `admin/admin_panel.py` — reescrito completo con HTTP
- `admin/.env` — configuración API_BASE y ADMIN_SECRET
- `backend/fix_duplicados.py` — script de limpieza de duplicados (ejecutar en PythonAnywhere)

---

## 14. Sistema de Control de Fechas en Curso (Charla 02)

### Objetivo

Implementar 8 controles para gestionar correctamente el ciclo de vida de una fecha de fútbol:

1. No jugar si la fecha ya comenzó (límite: hora del primer partido)
2. No jugar la siguiente fecha hasta que termine la actual
3. No jugar fecha anterior ni modificar jugada guardada
4. Botón "JUEGA BOLETA" solo habilitado si todos los partidos están marcados
5. Mostrar visualmente la fecha en curso con fibrón verde (aciertos) y naranja (errados)
6. Mini panel con porcentajes cuando la fecha está en curso
7. En "Mis Jugadas" NO mostrar aciertos calculados con resultados aleatorios — mostrar "EN CURSO"
8. Nueva tabla `resultados` con campos: id, nro_fecha, jugada_binaria, fecharegistro, pais, fecha_revision

### Archivos modificados

**`backend/models.py`**
- Nueva clase `ResultadoFecha` → tabla `resultados` con campos: `id`, `nro_fecha`, `jugada_binaria`, `fecha_registro`, `pais`, `fecha_revision`

**`backend/services.py`**
- `guardar_jugadas`: validación de fecha comenzada (primer partido) + validación de jugada duplicada por usuario/fecha
- `procesar_sorteo`: eliminada la generación de resultados aleatorios. Ahora solo calcula si TODOS los partidos tienen `resultado_real`

**`backend/app.py`**
- `/api/partidos` retorna `fecha_comenzada` (bool) y `primer_partido_hora`
- Nuevo endpoint `GET /api/mi-jugada-activa`: devuelve la jugada activa del usuario con detalle partido a partido, incluyendo `acierto_parcial` por partido
- `/api/admin/resultado`: cuando se carga el ÚLTIMO resultado de la fecha, calcula automáticamente los aciertos para TODAS las jugadas de esa fecha

**`frontend/src/components/Boleta.jsx`**
- Props nuevas: `fechaComenzada`, `yaJugo`
- Radios deshabilitados cuando la fecha está bloqueada
- Botón habilitado solo si `todosSeleccionados`
- Banners de estado visual

**`frontend/src/components/BoletaEnCurso.jsx`** _(nuevo)_
- Grid 6 columnas: `# | LOCAL | RESULTADO | VISITANTE | APUESTA | IND`
- Fibrón verde (`.bec-fibron--verde`) para aciertos parciales
- Fibrón naranja (`.bec-fibron--naranja`) para errados
- `MiniPanelStats` con barras de porcentaje de aciertos/desaciertos
- Auto-refresco cada 60s

**`frontend/src/App.jsx`**
- Estados: `fechaComenzada`, `jugadaActiva`
- Lógica: muestra `<BoletaEnCurso>` si `fechaComenzada && jugadaActiva`, sino `<Boleta>`
- `<PanelFixture>` dentro de `<div className="col-fixture">` (4ta columna)

**`frontend/src/components/PerfilHistorico.jsx`**
- Fix: muestra `"EN CURSO"` cuando `aciertos === null || aciertos === undefined` (evita mostrar aciertos calculados con método aleatorio)

**`frontend/src/index.css`**
- Layout migrado de flexbox a CSS Grid de 4 columnas explícitas:
  ```css
  .container {
      display: grid;
      grid-template-columns: minmax(320px, 580px) minmax(320px, 460px) minmax(280px, 360px) minmax(180px, 220px);
      gap: 1.5rem;
      max-width: 1680px;
  }
  ```
- Estilos BEC completos: `.bec-panel`, `.bec-fila`, `.bec-fibron--verde/naranja`, `.bec-stats`, etc.
- Eliminado bloque `@media (max-width: 992px)` incompatible con grid

### Scripts de mantenimiento creados

**`backend/migrate_resultados.py`** — crea la tabla `resultados` (ejecutar una vez en PythonAnywhere)

**`backend/limpiar_aciertos_viejos.py`** — pone NULL los aciertos calculados con resultados aleatorios en fechas anteriores a la activa

### Fix: "¿Por qué inventa resultados?"

`procesar_sorteo` tenía lógica legacy que generaba resultados aleatorios cuando no había resultados reales cargados. Esto causó que se grabaran aciertos incorrectos (ej. "11 DE 15 ACIERTOS") en la DB.

**Solución implementada:**
- `procesar_sorteo` ahora hace `return` inmediato si algún partido no tiene `resultado_real`
- Los aciertos reales solo se calculan desde `/api/admin/resultado` cuando el admin carga el último partido de la fecha
- Los aciertos viejos incorrectos se limpian con `limpiar_aciertos_viejos.py`

### Checklist para actualizar PythonAnywhere

```
[ ] Subir backend/app.py
[ ] Subir backend/models.py
[ ] Subir backend/services.py
[ ] Subir backend/migrate_resultados.py
[ ] Subir backend/limpiar_aciertos_viejos.py
[ ] Subir frontend/dist/index.html
[ ] Subir frontend/dist/assets/index-DlHM5QC5.css
[ ] Subir frontend/dist/assets/index-jcs2BC4E.js
[ ] python migrate_resultados.py          (crear tabla resultados)
[ ] python limpiar_aciertos_viejos.py     (limpiar aciertos falsos)
[ ] python fix_duplicados.py              (limpiar partidos duplicados)
[ ] Reload en panel Web
```

---

## 15. Próxima Fecha — Carga anticipada mientras la fecha activa está en curso (Charla 03)

### Contexto

En Argentina, la Fecha 10 se juega miércoles/jueves y la Fecha 11 arranca el viernes a las 18hs. El admin necesita poder cargar los partidos de la Fecha 11 mientras la Fecha 10 todavía está en curso, sin interferir con la fecha activa.

### Backend — Nuevo endpoint `/api/proxima-fecha`

Se agregó en `backend/app.py` (antes del endpoint `/api/jugada`):

```python
@app.route('/api/proxima-fecha', methods=['GET'])
def get_proxima_fecha():
    control = FechaActual.query.filter_by(activo=True).first()
    if not control:
        return jsonify({'proxima': None}), 200
    nro_proxima = control.nro_fecha + 1
    fecha = FechaSorteo.query.filter_by(nro_fecha=nro_proxima, pais_id=control.pais_id).first()
    if not fecha:
        return jsonify({'proxima': None}), 200
    partidos_lista = sorted(fecha.partidos, key=lambda x: x.orden)
    return jsonify({
        'proxima': {
            'nro_fecha': f"{fecha.nro_fecha:05d}",
            'fecha_id': fecha.id,
            'partidos': [
                {
                    'numero': i + 1,
                    'nombre': p.to_dict()['nombre'],
                    'local': p.equipo_local,
                    'visitante': p.equipo_visitante,
                    'fecha_hora': p.fecha_hora.isoformat() if getattr(p, 'fecha_hora', None) else None,
                }
                for i, p in enumerate(partidos_lista)
            ],
        }
    }), 200
```

### Frontend — Dos secciones en pantalla

**`frontend/src/App.jsx`:**
- Estados agregados: `proximaFecha`, `jugadasPendientesProxima`
- `fetchProximaFecha()` llamado al login junto con `fetchPartidos()`
- `handleJugarBoletasProxima()` para guardar jugadas de la próxima fecha
- JSX: ambas secciones (BoletaEnCurso/Boleta + proxima-fecha-wrap) envueltas en `<div className="col-izquierda">` para que el CSS grid las trate como una sola columna

```jsx
<div className="col-izquierda">
  {fechaComenzada && jugadaActiva ? (
    <BoletaEnCurso jugada={jugadaActiva} nroFecha={nroFecha} />
  ) : (
    <Boleta ... />
  )}
  {fechaComenzada && proximaFecha && (
    <div className="proxima-fecha-wrap">
      <div className="proxima-fecha-sep">📆 PRÓXIMA FECHA — ¡YA PODÉS JUGAR!</div>
      <Boleta partidos={proximaFecha.partidos} nroFecha={proximaFecha.nro_fecha} ... />
    </div>
  )}
</div>
```

**`frontend/src/index.css`:**
- `.col-izquierda { display: flex; flex-direction: column; gap: 1rem; min-width: 0; }` — nuevo
- `.bec-panel`: cambiado de `width: 580px; min-width: 380px` → `width: 100%; max-width: 580px; min-width: 0` (fix responsive)
- Grid de 4 columnas ajustado a `minmax(0, 520px) minmax(0, 420px) minmax(0, 340px) minmax(0, 220px)`
- `@media (max-width: 900px)`: colapsa a 1 columna
- `@media (max-width: 768px)`: padding mínimo, todo al 100%

### Panel Admin — Modo "Próxima Fecha"

**`admin/admin_panel.py`** — Sección "📅 Fechas & Fixture":
- Estado de sesión `st.session_state.viendo_proxima`
- Selector de país compartido entre tabs
- Dos botones: **"📅 FECHA ACTIVA #NNNNN"** y **"📆 PRÓXIMA FECHA #NNNNN"**
- Banner informativo según modo
- Los tres tabs (Activar Fecha, Ver Fixture, Nueva Fecha) pre-seleccionan la fecha correcta según el modo
- Sección "⚽ Resultados": selectbox muestra todas las fechas (no solo la activa), con caption "Próxima fecha — carga anticipada" cuando corresponde

### Checklist para actualizar PythonAnywhere

```
[ ] Subir backend/app.py         (nuevo endpoint /api/proxima-fecha)
[ ] Subir admin/admin_panel.py   (modo próxima fecha)
[ ] Subir frontend/dist/index.html
[ ] Subir frontend/dist/assets/  (js y css nuevos)
[ ] Reload en panel Web
```
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