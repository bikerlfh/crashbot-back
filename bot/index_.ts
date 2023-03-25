import * as dotenv from 'dotenv'
dotenv.config()
import {Game} from './src/game/Game'

import { HomeBets } from './src/constants';
import { Control } from './src/aviator/BetControl';
import {WebSocketClient} from './src/ws/client';

(async () => {
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
	// const websocketUrl = 'ws://localhost:8000/bot/';
	// const socket = new WebSocketClient(websocketUrl);
	// await socket.connect();
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
  })();
