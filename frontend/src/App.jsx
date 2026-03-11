import React, { useState, useEffect } from 'react';
import AuthScreen from './components/AuthScreen';
import Boleta from './components/Boleta';
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
  const [estadoSorteo, setEstadoSorteo] = useState('ESPERANDO');
  const [aciertos, setAciertos] = useState(0);

  // Estados para funcionalidad extendida
  const [jugadasPendientes, setJugadasPendientes] = useState([]);
  const [showModalCompra, setShowModalCompra] = useState(false);
  const [showModalCuenta, setShowModalCuenta] = useState(false);
  const [ticketADetalle, setTicketADetalle] = useState(null);

  // Se eliminó la carga automática de sesión para asegurar que el sistema "pare" en el login
  // como solicitó el usuario.
  useEffect(() => {
    // Mantener vacío o eliminar si no hay otros efectos de montaje
  }, []);

  useEffect(() => {
    if (usuario) {
      fetchPartidos();
      actualizarFichas();
    }
  }, [usuario?.dni]);

  const fetchPartidos = async () => {
    try {
      const resp = await fetch('/api/partidos');
      const data = await resp.json();
      if (resp.ok) {
        setPartidos(data.partidos || []);
        setNroFecha(data.nro_fecha || 0);
      }
    } catch (err) {
      console.error("Error fetching matches:", err);
    }
  };

  const actualizarFichas = async () => {
    if (!usuario) return;
    try {
      const resp = await fetchWithAuth(`/api/usuario/${usuario.dni}/fichas`);
      const data = await resp.json();
      if (resp.ok) {
        setUsuario(prev => ({ ...prev, fichas: data.fichas }));
      }
    } catch (err) {
      console.error("Error updating tokens:", err);
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

  const handleComprarFichas = async (paqueteId) => {
    try {
      const resp = await fetchWithAuth(`/api/iniciar-pago`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paquete: paqueteId })
      });
      const data = await resp.json();
      
      if (resp.ok && data.checkout_url) {
        if (data.modo === 'manual') {
          alert("Resumen: Al usar el link estático, el crédito de fichas es realizado MANUALMENTE por el administrador una vez confirmado el pago.\n\nSerás redirigido ahora.");
        }
        // Redirigir a Mercado Pago (o link estático)
        window.location.href = data.checkout_url;
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

        // Simular sorteo para la última jugada (id[0])
        const firstId = data.ids[0];
        setEstadoSorteo('SORTEANDO');

        // Petición de sorteo
        await fetchWithAuth('/api/sortear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ jugada_id: firstId })
        });

        // Polling corto para ver resultado
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

  if (!usuario) {
    return <AuthScreen onLogin={(u, token) => {
      setUsuario(u);
      sessionStorage.setItem('sabes_usuario', JSON.stringify(u));
      if (token) sessionStorage.setItem('jwt_token', token);
    }} />;
  }

  return (
    <main className="container">
      <Boleta
        partidos={partidos}
        nroFecha={nroFecha}
        usuarioDni={usuario.dni}
        fichas={usuario.fichas}
        pendientes={jugadasPendientes.length}
        onAgregarAlCarrito={(jugada) => setJugadasPendientes(prev => [...prev, jugada])}
        onJugar={handleJugarBoletas}
        onAbrirCompra={() => setShowModalCompra(true)}
      />

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
            onClose={() => setShowModalCompra(false)}
            onComprar={handleComprarFichas}
          />
        )}
        {showModalCuenta && (
          <MiCuentaModal
            usuario={usuario}
            onClose={() => setShowModalCuenta(false)}
            onActualizar={(nuevoU) => {
              setUsuario(nuevoU); // Actualiza estado global
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

      <PanelFixture nroFecha={nroFecha} />


      {ticketADetalle && (
        <TicketModal
          ticket={ticketADetalle}
          dni={usuario.dni}
          onClose={() => setTicketADetalle(null)}
        />
      )}
    </main>
  );
}

export default App;
