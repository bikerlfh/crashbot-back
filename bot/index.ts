import * as dotenv from 'dotenv'
dotenv.config()
import {Game} from './src/game/GameAdvance'
import {HomeBets } from './src/constants';
import {BotType} from './src/game/core';


(async () => {
	let readlineSync = require('readline-sync');
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
	autoPlay = autoPlay == "y"
	if(autoPlay){
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
	const game = new Game(homeBet, autoPlay, botTypeSelected, true)
	try{
		await game.initialize()
		await game.play()
	}catch(e){
		console.log(e)
	}
})();
