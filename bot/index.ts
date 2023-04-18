import * as dotenv from 'dotenv'
dotenv.config()
import {Game} from './src/game/GameAdvance'
import {HomeBets } from './src/constants';
import {BotType} from './src/game/core';
import { AviatorBotAPI } from './src/api/AviatorBotAPI';
import { HTTPStatus } from './src/api/constants';
import { LocalStorage } from 'node-localstorage';

const readlineSync = require('readline-sync');

const localStorage = new LocalStorage('./storage');

async function login(): Promise<boolean> {
	const token = localStorage.getItem('token')
	const refresh = localStorage.getItem('refresh')
	if(token){
		const response = await AviatorBotAPI.requestTokenVerify(token)
		if(response.status == HTTPStatus.OK){
			console.log("login success")
			return true
		}
	}else if(refresh){
		const response = await AviatorBotAPI.requestTokenRefresh(refresh)
		if(response.status == HTTPStatus.OK){
			localStorage.setItem('token', response.data.access);
			console.log("login success")
			return true
		}
	}
	const username = readlineSync.question('username: ');
	const password = readlineSync.question('password: ', {
		hideEchoBack: true // The typed text on screen is hidden by `*` (default).
	});
	const response = await AviatorBotAPI.requestLogin(username, password)
	if(response.status == HTTPStatus.UNAUTHORIZED){
		console.log("invalid credentials")
		return false
	}	
	localStorage.setItem('token', response.data.access);
	localStorage.setItem('refresh', response.data.refresh);
	console.log("login success")
	return true
}

(async () => {
	let isAuthenticated= false
	do{
		isAuthenticated = await login()
	}while(!isAuthenticated);
	const homeBetSelected = readlineSync.question(
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
	let _botTypeSelected = "2"
	let botTypeSelected = BotType.TIGHT
	let autoPlay = readlineSync.question("automatic play? [y/n]: ");
	(global as any).autoPlay = autoPlay == "y"
	if((global as any).autoPlay){
		_botTypeSelected = readlineSync.question(
			"which player type do you choose (default: tight)? [aggressive=1, tight=2, loose=3]: "
		);
	}
	switch(_botTypeSelected){
		case "1":
			botTypeSelected = BotType.AGGRESSIVE
			break;
		case "3":
			botTypeSelected = BotType.LOOSE
			break;
		default:
			botTypeSelected = BotType.TIGHT
	}
	console.clear()
	const game = new Game(homeBet, botTypeSelected, true)
	try{
		await game.initialize()
		await game.play()
	}catch(e){
		console.log(e)
	}
})();
