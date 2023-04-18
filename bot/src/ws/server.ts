import { createServer } from 'http';
import { Server, Socket } from 'socket.io';

const httpServer = createServer();
const io = new Server(httpServer);

io.on('connection', (socket: Socket) => {
  console.log('Nuevo cliente conectado');
  // Escuchar eventos de mensajes recibidos
  socket.on('mensaje', (data: any) => {
    console.log(`Mensaje recibido: ${data}`);
    // Emitir el mensaje recibido a todos los clientes conectados
    io.emit('mensaje', data);
  });
});

httpServer.listen(3000, () => {
  console.log('Servidor escuchando en el puerto 3000');
});