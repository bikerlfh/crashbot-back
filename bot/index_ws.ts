import { createServer } from 'http';
import { Server, Socket } from 'socket.io';
import {
    loginEvent,
    verifyTokenEvent, 
    autoPlayEvent, 
    startBotEvent, 
    closeGameEvent, 
    setMaxAmountToBetEvent
} from "./src/ws/events";
import {createGlobals} from "./src/globals";

const httpServer = createServer();
const io = new Server(httpServer);

createGlobals(io);

let numConnections = 0;
const maxConnections = 2; // Máximo de conexiones permitidas

// Middleware para limitar el número de conexiones
io.use((socket, next) => {
    if (numConnections >= maxConnections) {
        return next(new Error('Demasiadas conexiones'));
    }
    numConnections++;
    socket.on('disconnect', () => {
        console.log('ws client disconnected');
        numConnections--;
        closeGameEvent().then((response: any) => {
            socket.emit('closeGame', response)
        }).catch((error: any) => {
            socket.emit('closeGame', error)
        });
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
        console.log('login', data)
        loginEvent(data).then((response: any) => {
            socket.emit('login', response)
        }).catch((error: any) => { 
            socket.emit('login', JSON.stringify(error))
        });
    });
    socket.on('startBot', (data: any) => {
        startBotEvent(data, socket).catch((error: any) => {
            socket.emit('startBot', error)
        });
    });
    socket.on('autoPlay', (data: any) => {
        const msg = autoPlayEvent(data)
        socket.emit('autoPlay', msg)
    });
    socket.on('setMaxAmountToBet', (data: any) => {
        const msg = setMaxAmountToBetEvent(data)
        socket.emit('setMaxAmountToBet', msg)
    });
    socket.on('closeGame', (data: any) => {
        closeGameEvent().then((response: any) => {
            socket.emit('closeGame', response)
        }).catch((error: any) => {
            socket.emit('closeGame', error)
        });
    });
});

httpServer.listen(3000, () => {
    console.log('server running on port 3000');
});