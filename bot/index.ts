import * as dotenv from 'dotenv'
dotenv.config()
import {Game} from './src/game/GameAdvance'
import {HomeBets } from './src/constants';
import {PlayerType} from './src/game/player';


(async () => {
	let readlineSync = require('readline-sync');
	let autoPlay = readlineSync.question("automatic play? [y/n]: ");
	autoPlay = autoPlay == "y"
	const homeBetSelected = readlineSync.question(
		"which bookmaker do you choose (default: demo)? [betPlay=1, 1Win=2]: "
	);
	let playerTypeSelected = readlineSync.question(
		"which player type do you choose (default: tight)? [aggressive=1, tight=2, loose=3]: "
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
	switch(playerTypeSelected){
		case "1":
			playerTypeSelected = PlayerType.AGGRESSIVE
			break;
		case "3":
			playerTypeSelected = PlayerType.LOOSE
			break;
		default:
			playerTypeSelected = PlayerType.TIGHT
	}
	console.clear()
	while(true){
		try{
			const game = new Game(homeBet, autoPlay, playerTypeSelected)
			await game.initialize()
			await game.play()
		}catch(e){
			console.log(e)
		}
	}
})();
