const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*", // Aceptar desde React (localhost:5173 usualmente)
        methods: ["GET", "POST"]
    }
});

const PARTIDOS_BASE = [
    "BOCA - RIVER",
    "RACING - INDEPTE",
    "SAN LORENZO - HURACAN",
    "ESTUDIANTES - GIMNASIA",
    "ROSARIO CTRAL - NEWELLS",
    "VELEZ - FERRO",
    "ARGENTINOS - PLATENSE",
    "LANUS - BANFIELD",
    "COLON - UNION",
    "TALLERES - BELGRANO",
    "CHACARITA - ATLANTA",
    "NUEVA CHICAGO - ALL BOYS",
    "DEF. BELGRANO - EXCURSION"
];

// Opciones L = Local, X = Empate, V = Visitante
const OPCIONES = ['L', 'X', 'V'];

// Genera una ronda de partidos
function generarPartidos() {
    return PARTIDOS_BASE.map((partido, index) => {
        return {
            id: index + 1,
            nombre: partido,
            resultado_final: null, // Se llenará en el sorteo
        };
    });
}

let estadoSorteo = {
    activo: false,
    partidos: generarPartidos(),
    partidoActual: 0,
};

io.on('connection', (socket) => {
    console.log('Cliente conectado:', socket.id);

    // Al conectar, enviamos el estado inicial
    socket.emit('estado_inicial', estadoSorteo.partidos);

    // Cuando un cliente pide jugar
    socket.on('iniciar_sorteo', (boletaUsuario) => {
        if (estadoSorteo.activo) {
            socket.emit('error', 'Ya hay un sorteo en curso.');
            return;
        }

        console.log("Iniciando sorteo...", boletaUsuario);
        estadoSorteo.activo = true;
        estadoSorteo.partidos = generarPartidos(); // Reset
        estadoSorteo.partidoActual = 0;

        io.emit('sorteo_iniciado');

        // Simulamos un sorteo cada x segundos
        let interval = setInterval(() => {
            if (estadoSorteo.partidoActual >= estadoSorteo.partidos.length) {
                clearInterval(interval);
                estadoSorteo.activo = false;

                // Calcular aciertos y emitir fin
                let aciertos = 0;
                boletaUsuario.forEach((apuesta, idx) => {
                    if (apuesta === estadoSorteo.partidos[idx].resultado_final) {
                        aciertos++;
                    }
                });

                socket.emit('sorteo_finalizado', { aciertos, resultados: estadoSorteo.partidos });
                return;
            }

            // Sortea un partido
            const idx = estadoSorteo.partidoActual;
            const resAleatorio = OPCIONES[Math.floor(Math.random() * OPCIONES.length)];
            estadoSorteo.partidos[idx].resultado_final = resAleatorio;

            // Emitir evento con confeti si es un partido importante, o solo el resultado
            io.emit('partido_resultado', {
                partido_idx: idx,
                resultado: resAleatorio,
                nombre: estadoSorteo.partidos[idx].nombre
            });

            estadoSorteo.partidoActual++;
        }, 1200); // 1.2 segundos por partido
    });

    socket.on('disconnect', () => {
        console.log('Cliente desconectado:', socket.id);
    });
});

const PORT = 3001;
server.listen(PORT, () => {
    console.log(`Servidor Socket.io corriendo en el puerto ${PORT}`);
});
