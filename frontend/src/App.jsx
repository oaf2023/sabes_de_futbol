import { useState, useEffect } from 'react';
import AuthScreen from './components/AuthScreen';
import Boleta from './components/Boleta';
import BoletaEnCurso from './components/BoletaEnCurso';
import PanelSorteo from './components/PanelSorteo';
import TablaPremios from './components/TablaPremios';
import PerfilHistorico from './components/PerfilHistorico';
import PerfilJugador from './components/PerfilJugador';
import TicketModal from './components/TicketModal';
import CompraFichasModal from './components/CompraFichasModal';
import MiCuentaModal from './components/MiCuentaModal';
import PanelFixture from './components/PanelFixture';
import { fetchWithAuth } from './utils/fetchWithAuth';

function App() {
  const [usuario, setUsuario] = useState(null);
  const [partidos, setPartidos] = useState([]);
  const [nroFecha, setNroFecha] = useState(0);
  const [fechaComenzada, setFechaComenzada] = useState(false);
  const [estadoSorteo, setEstadoSorteo] = useState('ESPERANDO');
  const [aciertos, setAciertos] = useState(0);

  // Jugada activa del usuario en la fecha en curso
  const [jugadaActiva, setJugadaActiva] = useState(null);

  const [proximaFecha, setProximaFecha] = useState(null); // { nro_fecha, partidos[] }
  const [jugadasPendientesProxima, setJugadasPendientesProxima] = useState([]);

  const [jugadasPendientes, setJugadasPendientes] = useState([]);
  const [showModalCompra, setShowModalCompra] = useState(false);
  const [showModalCuenta, setShowModalCuenta] = useState(false);
  const [ticketADetalle, setTicketADetalle] = useState(null);
  const [mensajePago, setMensajePago] = useState(null);
  const [ahora, setAhora] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setAhora(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Detectar retorno desde MercadoPago (?pago=success|failure|pending)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const estadoPago = params.get('pago');
    if (!estadoPago) return;
    window.history.replaceState({}, '', '/');
    if (estadoPago === 'success') {
      setMensajePago({ tipo: 'success', texto: '¡Pago aprobado! Tus fichas fueron acreditadas.' });
      // Polling: el webhook puede tardar unos segundos en acreditar
      let intentos = 0;
      const poll = setInterval(async () => {
        intentos++;
        try {
          const resp = await fetchWithAuth('/api/usuario/estado-ultimo-pago');
          const data = await resp.json();
          if (data.estado === 'aprobado' || intentos >= 4) {
            clearInterval(poll);
            // Refrescar fichas del usuario
            const u = JSON.parse(sessionStorage.getItem('sabes_usuario') || '{}');
            if (u.dni) {
              const r2 = await fetchWithAuth(`/api/usuario/${u.dni}/fichas`);
              const d2 = await r2.json();
              if (r2.ok) setUsuario(prev => prev ? { ...prev, fichas: d2.fichas } : prev);
            }
          }
        } catch { clearInterval(poll); }
      }, 2000);
    } else if (estadoPago === 'pending') {
      setMensajePago({ tipo: 'pending', texto: 'Pago pendiente de confirmación. Las fichas se acreditarán cuando se apruebe.' });
    } else if (estadoPago === 'failure') {
      setMensajePago({ tipo: 'failure', texto: 'El pago no pudo completarse. Podés intentarlo de nuevo.' });
    }
  }, []);

  useEffect(() => {
    if (usuario) {
      fetchPartidos();
      fetchProximaFecha();
      actualizarFichas();
    }
  }, [usuario?.dni]);

  // Cuando la fecha está en curso, actualizar jugadaActiva cada 60s
  useEffect(() => {
    if (!usuario || !fechaComenzada) return;
    fetchJugadaActiva();
    const t = setInterval(fetchJugadaActiva, 60_000);
    return () => clearInterval(t);
  }, [usuario?.dni, fechaComenzada]);

  const fetchPartidos = async () => {
    try {
      const resp = await fetch('/api/partidos');
      const data = await resp.json();
      if (resp.ok) {
        setPartidos(data.partidos || []);
        setNroFecha(data.nro_fecha || 0);
        setFechaComenzada(data.fecha_comenzada || false);
        // Si la fecha comenzó, traer la jugada activa inmediatamente
        if (data.fecha_comenzada) {
          fetchJugadaActiva();
        }
      }
    } catch (err) {
      console.error("Error fetching matches:", err);
    }
  };

  const fetchProximaFecha = async () => {
    try {
      const resp = await fetch('/api/proxima-fecha');
      const data = await resp.json();
      setProximaFecha(data.proxima || null);
    } catch (err) {
      console.error("Error fetching proxima fecha:", err);
    }
  };

  const fetchJugadaActiva = async () => {
    try {
      const resp = await fetchWithAuth('/api/mi-jugada-activa');
      const data = await resp.json();
      if (resp.ok && data.jugada) {
        setJugadaActiva(data.jugada);
      } else {
        setJugadaActiva(null);
      }
    } catch (err) {
      console.error("Error fetching jugada activa:", err);
    }
  };

  const actualizarFichas = async () => {
    if (!usuario) return;
    try {
      const resp = await fetchWithAuth(`/api/usuario/${usuario.dni}/fichas`);
      const data = await resp.json();
      if (resp.ok) {
        setUsuario(prev => {
          const actualizado = { ...prev, fichas: data.fichas };
          sessionStorage.setItem('sabes_usuario', JSON.stringify(actualizado));
          return actualizado;
        });
      }
    } catch (err) {
      console.error("Error updating fichas:", err);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('sabes_usuario');
    sessionStorage.removeItem('jwt_token');
    setUsuario(null);
    window.location.reload();
  };

  const handleVerTicket = async (id) => {
    try {
      const resp = await fetchWithAuth(`/api/jugada/${id}`);
      const data = await resp.json();
      if (resp.ok) {
        setTicketADetalle(data);
      } else {
        alert(data.error || "Error al obtener detalle");
      }
    } catch (err) {
      console.error("Error fetch ticket:", err);
    }
  };

  const handleComprarFichas = async (cantidad) => {
    try {
      const resp = await fetchWithAuth(`/api/iniciar-pago`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cantidad })
      });
      const data = await resp.json();

      if (resp.ok && data.checkout_url) {
        if (data.modo === 'manual') {
          alert("El crédito de fichas será realizado MANUALMENTE por el administrador una vez confirmado el pago.");
        }
        // Abrir MP en pestaña nueva, la app queda abierta
        window.open(data.checkout_url, '_blank');
        setShowModalCompra(false);
        setMensajePago({ tipo: 'pending', texto: 'Completá el pago en la pestaña de Mercado Pago. Las fichas se acreditarán automáticamente.' });

        // Polling: chequear este pago específico cada 3s hasta 2 minutos
        const pagoId = data.pago_id;
        const endpoint = pagoId
          ? `/api/usuario/pago/${pagoId}`
          : '/api/usuario/estado-ultimo-pago';
        let intentos = 0;
        const poll = setInterval(async () => {
          intentos++;
          try {
            const r = await fetchWithAuth(endpoint);
            const d = await r.json();
            if (d.estado === 'aprobado') {
              clearInterval(poll);
              await actualizarFichas();
              setMensajePago({ tipo: 'success', texto: `¡Fichas acreditadas! +${d.fichas} fichas en tu cuenta.` });
            } else if (intentos >= 40) {
              clearInterval(poll);
              setMensajePago(null);
            }
          } catch { clearInterval(poll); }
        }, 3000);
      } else {
        alert(data.error || "Error al iniciar el pago. Por favor, intenta de nuevo más tarde.");
      }
    } catch (err) {
      console.error("Error initiating payment:", err);
      alert("Error al conectar con el servidor de pagos.");
    }
  };

  const handleJugarBoletas = async (ultimaBoleta) => {
    const todas = [...jugadasPendientes, ultimaBoleta];
    const costo = todas.length;

    if (usuario.fichas < costo) {
      alert(`❌ Fichas insuficientes. Necesitás ${costo} fichas.`);
      return;
    }

    try {
      const resp = await fetchWithAuth('/api/jugada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jugadas: todas })
      });
      const data = await resp.json();
      if (resp.ok) {
        setJugadasPendientes([]);
        actualizarFichas();
        // Refrescar jugada activa tras jugar
        fetchJugadaActiva();

        const firstId = data.ids[0];
        setEstadoSorteo('SORTEANDO');

        await fetchWithAuth('/api/sortear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ jugada_id: firstId })
        });

        setTimeout(async () => {
          const respDetalle = await fetchWithAuth(`/api/jugada/${firstId}`);
          const dataDetalle = await respDetalle.json();
          if (respDetalle.ok && dataDetalle.status === 'completado') {
            setAciertos(dataDetalle.aciertos);
            setEstadoSorteo('FINALIZADO');
            setTicketADetalle(dataDetalle);
          }
        }, 3000);

      } else {
        alert(data.error || "Error al guardar jugadas");
      }
    } catch (err) {
      console.error("Error playing:", err);
    }
  };

  const handleJugarBoletasProxima = async (ultimaBoleta) => {
    const todas = [...jugadasPendientesProxima, ultimaBoleta];
    const costo = todas.length;

    if (usuario.fichas < costo) {
      alert(`❌ Fichas insuficientes. Necesitás ${costo} fichas.`);
      return;
    }

    try {
      const resp = await fetchWithAuth('/api/jugada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jugadas: todas, fecha_sorteo_id: proximaFecha.fecha_id })
      });
      const data = await resp.json();
      if (resp.ok) {
        setJugadasPendientesProxima([]);
        actualizarFichas();
        alert(`✅ Jugada para la Fecha #${proximaFecha.nro_fecha} guardada con éxito.`);
      } else {
        alert(data.error || "Error al guardar jugadas");
      }
    } catch (err) {
      console.error("Error playing proxima:", err);
    }
  };

  if (!usuario) {
    return <AuthScreen onLogin={(u, token) => {
      setUsuario(u);
      sessionStorage.setItem('sabes_usuario', JSON.stringify(u));
      if (token) sessionStorage.setItem('jwt_token', token);
    }} />;
  }

  // El usuario ya tiene jugada guardada en la fecha activa
  const yaJugo = jugadaActiva !== null;

  const optsZona = { timeZone: 'America/Argentina/Buenos_Aires' };
  const fechaStr = ahora.toLocaleDateString('es-AR', { ...optsZona, weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' }).toUpperCase();
  const horaStr  = ahora.toLocaleTimeString('es-AR', { ...optsZona, hour: '2-digit', minute: '2-digit', second: '2-digit' });

  return (
    <>
    <header className="app-header">
      <img src="/logo.png" alt="Sabes de Fútbol" className="app-header-logo" />
      <div className="app-header-reloj">
        <span className="app-header-fecha">{fechaStr}</span>
        <span className="app-header-hora">{horaStr}</span>
      </div>
    </header>
    <main className="container">
      {mensajePago && (
        <div className={`banner-pago banner-pago--${mensajePago.tipo}`}>
          <span>{mensajePago.texto}</span>
          <button className="banner-pago-cerrar" onClick={() => setMensajePago(null)}>✕</button>
        </div>
      )}
      {/* Columna izquierda: boleta para jugar (si no comenzó) o boleta en curso + próxima fecha */}
      <div className="col-izquierda">
        {fechaComenzada && jugadaActiva ? (
          <BoletaEnCurso jugada={jugadaActiva} nroFecha={nroFecha} />
        ) : (
          <Boleta
            partidos={partidos}
            nroFecha={nroFecha}
            usuarioDni={usuario.dni}
            fichas={usuario.fichas}
            pendientes={jugadasPendientes.length}
            fechaComenzada={fechaComenzada}
            yaJugo={yaJugo}
            onAgregarAlCarrito={(jugada) => setJugadasPendientes(prev => [...prev, jugada])}
            onJugar={handleJugarBoletas}
            onAbrirCompra={() => setShowModalCompra(true)}
          />
        )}

        {/* Próxima fecha: visible cuando la fecha activa comenzó (o el usuario ya tiene jugada) y existe fixture cargado */}
        {(fechaComenzada || jugadaActiva) && proximaFecha && (
          <div className="proxima-fecha-wrap">
            <div className="proxima-fecha-sep">📆 PRÓXIMA FECHA — ¡YA PODÉS JUGAR!</div>
            <Boleta
              partidos={proximaFecha.partidos}
              nroFecha={proximaFecha.nro_fecha}
              usuarioDni={usuario.dni}
              fichas={usuario.fichas}
              pendientes={jugadasPendientesProxima.length}
              fechaComenzada={false}
              yaJugo={false}
              onAgregarAlCarrito={(jugada) => setJugadasPendientesProxima(prev => [...prev, jugada])}
              onJugar={handleJugarBoletasProxima}
              onAbrirCompra={() => setShowModalCompra(true)}
            />
          </div>
        )}
      </div>

      <div className="col-central" style={{ position: 'relative' }}>
        <PerfilJugador
          usuario={usuario}
          onLogout={handleLogout}
          onAbrirCuenta={() => setShowModalCuenta(true)}
        />
        <PanelSorteo
          partidos={partidos}
          estadoSorteo={estadoSorteo}
        />
        {showModalCompra && (
          <CompraFichasModal
            fichasActuales={usuario?.fichas || 0}
            onClose={() => setShowModalCompra(false)}
            onComprar={handleComprarFichas}
          />
        )}
        {showModalCuenta && (
          <MiCuentaModal
            usuario={usuario}
            onClose={() => setShowModalCuenta(false)}
            onActualizar={(nuevoU) => {
              setUsuario(nuevoU);
              sessionStorage.setItem('sabes_usuario', JSON.stringify(nuevoU));
            }}
          />
        )}
      </div>

      <div className="col-derecha">
        <TablaPremios
          estadoSorteo={estadoSorteo}
          aciertos={aciertos}
        />
        <PerfilHistorico
          usuario={usuario}
          onVerTicket={handleVerTicket}
        />
      </div>

      <div className="col-fixture">
        <PanelFixture nroFecha={nroFecha} />
      </div>

      {ticketADetalle && (
        <TicketModal
          ticket={ticketADetalle}
          dni={usuario.dni}
          onClose={() => setTicketADetalle(null)}
        />
      )}
    </main>
    </>
  );
}

export default App;
