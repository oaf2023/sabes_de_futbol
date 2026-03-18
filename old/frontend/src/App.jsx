import { useEffect, useState } from 'react'
import Boleta from './components/Boleta'
import PanelSorteo from './components/PanelSorteo'
import TablaPremios from './components/TablaPremios'
import PerfilHistorico from './components/PerfilHistorico'
import AuthScreen from './components/AuthScreen'

function App() {
  const [partidos, setPartidos] = useState([]);
  const [estadoSorteo, setEstadoSorteo] = useState('ESPERANDO'); // ESPERANDO, SORTEANDO, FINALIZADO
  const [boletaUsuario, setBoletaUsuario] = useState(Array(13).fill(null));
  const [aciertos, setAciertos] = useState(0);
  const [usuario, setUsuario] = useState(null);
  const [loading, setLoading] = useState(false);

  // Cargar estado inicial
  useEffect(() => {
    if (usuario) {
      obtenerPartidos();
    }
  }, [usuario]);

  const obtenerPartidos = async () => {
    try {
      const resp = await fetch('/api/partidos');
      const data = await resp.json();
      if (resp.ok) {
        // Mapear partidos para que tengan el formato que espera el frontend
        const partidosFormateados = data.partidos.map(p => ({
          nombre: p.nombre,
          resultado_final: null // Inicialmente nulo hasta el sorteo
        }));
        setPartidos(partidosFormateados);
      }
    } catch (err) {
      console.error("Error cargando partidos:", err);
    }
  };

  const handleJugar = async () => {
    if (boletaUsuario.includes(null)) {
      alert("Completá todos los partidos, che!");
      return;
    }

    setLoading(true);
    try {
      // 1. Guardar la jugada
      const respJugada = await fetch('/api/jugada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dni: usuario.dni, jugadas: [boletaUsuario] })
      });
      const dataJugada = await respJugada.json();

      if (!respJugada.ok) throw new Error(dataJugada.error);

      const jugadaId = dataJugada.jugadas_ids[0];

      // 2. Iniciar sorteo
      const respSorteo = await fetch('/api/sortear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jugada_id: jugadaId })
      });

      if (!respSorteo.ok) throw new Error("Error al iniciar sorteo");

      setEstadoSorteo('SORTEANDO');

      // 3. Polling para obtener resultados
      pollResultados(jugadaId);

    } catch (err) {
      alert("Error: " + err.message);
      setLoading(false);
    }
  };

  const pollResultados = async (jugadaId) => {
    const interval = setInterval(async () => {
      try {
        const resp = await fetch(`/api/jugada/${jugadaId}`);
        const data = await resp.json();

        if (data.status === 'completado') {
          clearInterval(interval);
          setAciertos(data.aciertos);
          // Actualizar partidos con los resultados reales
          const nuevosPartidos = data.partidos.map(p => ({
            nombre: p.nombre,
            resultado_final: p.resultado
          }));
          setPartidos(nuevosPartidos);
          setEstadoSorteo('FINALIZADO');
          setLoading(false);

          // Actualizar saldo de fichas del usuario localmente
          setUsuario(prev => ({ ...prev, fichas: prev.fichas - 1 }));
        }
      } catch (err) {
        console.error("Error en polling:", err);
      }
    }, 2000);
  };

  const setApuesta = (index, valor) => {
    if (estadoSorteo === 'SORTEANDO' || loading) return;
    const nueva = [...boletaUsuario];
    nueva[index] = valor;
    setBoletaUsuario(nueva);
  };

  if (!usuario) {
    return <AuthScreen onLogin={setUsuario} />
  }

  return (
    <main className="container">
      <Boleta
        partidos={partidos}
        boletaUsuario={boletaUsuario}
        setApuesta={setApuesta}
        handleJugar={handleJugar}
        estadoSorteo={estadoSorteo}
        loading={loading}
      />

      <div className="col-central" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', width: '380px', minWidth: '320px' }}>
        <PerfilHistorico usuario={usuario} />
        <PanelSorteo
          partidos={partidos}
          estadoSorteo={estadoSorteo}
          loading={loading}
        />
      </div>

      <TablaPremios
        estadoSorteo={estadoSorteo}
        aciertos={aciertos}
      />
    </main>
  )
}

export default App
