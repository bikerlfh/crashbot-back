import { createServer } from 'http';
import { Server, Socket } from 'socket.io';
import {loginEvent, verifyTokenEvent, autoPlayEvent, startBotEvent, closeGameEvent} from "./src/ws/events";
import {createGlobals} from "./src/globals";

const httpServer = createServer();
const io = new Server(httpServer);

createGlobals(io);

let numConnections = 0;
const maxConnections = 1; // Máximo de conexiones permitidas

// Middleware para limitar el número de conexiones
io.use((socket, next) => {
    if (numConnections >= maxConnections) {
        return next(new Error('Demasiadas conexiones'));
    }
    numConnections++;
    socket.on('disconnect', () => {
        console.log('ws client disconnected');
        numConnections--;
    });
    next();
});

io.on('connection', (socket: Socket) => {
    console.log('ws client connected');
    socket.on('verify', (data: any) => {
        verifyTokenEvent().then((response: any) => {
            socket.emit('verify', response)
        }).catch((error: any) => {
            socket.emit('verify', error)
        })
    });
    socket.on('login', (data: any) => {
        loginEvent(data).then((response: any) => {
            socket.emit('login', response)
        }).catch((error: any) => {
            console.log("errr", error)
            socket.emit('login', JSON.stringify(error))
        });
    });
    socket.on('startBot', (data: any) => {
        startBotEvent(data).catch((error: any) => {
            socket.emit('startBot', error)
        });
    });
    socket.on('autoPlay', (data: any) => {
        const msg = autoPlayEvent(data)
        socket.emit('autoPlay', msg)
    });
    socket.on('setMaxAmountToBet', (data: any) => {
        const msg = autoPlayEvent(data)
        socket.emit('autoPlay', msg)
    });
    socket.on('closeGame', (data: any) => {
        closeGameEvent(data).then((response: any) => {
            socket.emit('closeGame', response)
        }).catch((error: any) => {
            socket.emit('closeGame', error)
        });
    });
});

httpServer.listen(3000, () => {
    console.log('Servidor escuchando en el puerto 3000');
});