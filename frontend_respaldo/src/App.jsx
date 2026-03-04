import { useEffect, useState } from 'react'
import io from 'socket.io-client'
import Boleta from './components/Boleta'
import PanelSorteo from './components/PanelSorteo'
import TablaPremios from './components/TablaPremios'
import PerfilHistorico from './components/PerfilHistorico'
import AuthScreen from './components/AuthScreen'

// Conexión al backend
const socket = io('http://localhost:3001');

function App() {
  const [partidos, setPartidos] = useState([]);
  const [estadoSorteo, setEstadoSorteo] = useState('ESPERANDO'); // ESPERANDO, SORTEANDO, FINALIZADO
  const [boletaUsuario, setBoletaUsuario] = useState(Array(13).fill(null));
  const [aciertos, setAciertos] = useState(0);
  const [usuario, setUsuario] = useState(null);

  useEffect(() => {
    socket.on('estado_inicial', (data) => {
      setPartidos(data);
    });

    socket.on('sorteo_iniciado', () => {
      setEstadoSorteo('SORTEANDO');
    });

    socket.on('partido_resultado', (data) => {
      setPartidos(prev => {
        const nuevos = [...prev];
        nuevos[data.partido_idx].resultado_final = data.resultado;
        return nuevos;
      });
    });

    socket.on('sorteo_finalizado', (data) => {
      setEstadoSorteo('FINALIZADO');
      setAciertos(data.aciertos);
      setPartidos(data.resultados);
    });

    return () => {
      socket.off('estado_inicial');
      socket.off('sorteo_iniciado');
      socket.off('partido_resultado');
      socket.off('sorteo_finalizado');
    };
  }, []);

  const handleJugar = () => {
    // Validar boleta completa
    if (boletaUsuario.includes(null)) {
      alert("Completá todos los partidos, che!");
      return;
    }
    socket.emit('iniciar_sorteo', boletaUsuario);
  };

  const setApuesta = (index, valor) => {
    if (estadoSorteo === 'SORTEANDO') return;
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
      />

      <div className="col-central" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', width: '380px', minWidth: '320px' }}>
        <PerfilHistorico />
        <PanelSorteo
          partidos={partidos}
          estadoSorteo={estadoSorteo}
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
