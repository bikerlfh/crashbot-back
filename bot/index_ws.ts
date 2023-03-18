import * as dotenv from 'dotenv'
import WebSocket from 'ws';
import express from 'express'
import { Server, Socket } from 'socket.io';
import http from 'http';
dotenv.config()
import {Game} from './src/game/Game'

import { HomeBets } from './src/constants';
import { Control } from './src/aviator/BetControl';

const app = express();
const server = http.createServer(app);
const io = new Server(server);


class WebSocketClient {
    private socket: WebSocket;

    constructor(url: string) {
        this.socket = new WebSocket(url);

        this.socket.addEventListener('open', (event: any) => {
            console.log('WebSocket connected:', event);
        });

        this.socket.addEventListener('message', (event: any) => {
            console.log('WebSocket message received:', event.data);
        });

        this.socket.addEventListener('close', (event: any) => {
            console.log('WebSocket closed:', event);
        });

        this.socket.addEventListener('error', (event: any) => {
            console.error('WebSocket error:', event);
        });
    }

    public sendMessage(message: string): void {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(message);
        } else {
            console.error('WebSocket is not open. Ready state:', this.socket.readyState);
        }
    }
}

// Replace 'ws://your-websocket-url' with the URL of your WebSocket server
const websocketUrl = 'ws://localhost:8000/ws/chat/';
const client = new WebSocketClient(websocketUrl);

// Wait for the connection to be established, then send a message
setTimeout(() => {
    client.sendMessage('Hello, WebSocket server!');
}, 1000);
/*

io.on('connection', (socket: Socket) => {
    console.log(`Usuario conectado: ${socket.id}`);

    socket.on('message', (message) => {
        console.log(`Mensaje recibido: ${message}`);
        io.emit('message', message);
    });

    socket.on('disconnect', () => {
        console.log(`Usuario desconectado: ${socket.id}`);
    });
});

const port = 5000;
server.listen(port, () => {
    console.log(`Servidor de SocketIO escuchando en el puerto ${port}`);
});
*/

const openBot = async () => {
	let readlineSync = require('readline-sync');
	let automaticPlay = readlineSync.question("automatic play? [y/n]: ");
	automaticPlay = automaticPlay == "y"
	let homeBetSelected = readlineSync.question(
		"which bookmaker do you choose (default: demo)? [betPlay=1, 1Win=2]: "
	);
	let homeBet = HomeBets.demo
	switch(homeBetSelected){
		case "1":
			homeBet = HomeBets.betplay
			break;
		case "2":
			homeBet = HomeBets.oneWin
			break;
		default:
			homeBet = HomeBets.demo
	}
	console.clear()
	console.log("opening home bet.....")
	const aviatorPage = homeBet.aviatorPage
	await aviatorPage.open()
	console.clear()
	const game = new Game(
		homeBet, 
		aviatorPage.multipliers,
		aviatorPage.balance
	)
	const initialBalance = game.balance
	const sleepNow = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay))
	while(true){
		await aviatorPage.waitNextGame()
		const balance = await aviatorPage.readBalance()
		game.addMultiplier(aviatorPage.multipliers.slice(-1)[0])
		if(balance != null){
			game.balance = balance
		}
		const profit = game.balance - initialBalance
		if(profit > 0){
			game.initialBalance = game.balance
		}
		console.log("real profit:", profit)
		const bets = await game.getNextBet()
		if(bets.length){
			console.log("bets:", bets)
			if(automaticPlay == false){
				continue
			}
			for (let index = 0; index < bets.length; index++) {
				const bet = bets[index];
				const control = index == 0? Control.Control1: Control.Control2
				await aviatorPage.bet(bet.amount, bet.multiplier, control)
				await sleepNow(2000)
			}
		}
	}
};

// openBot();