import * as dotenv from 'dotenv'
dotenv.config()
import {Game} from './src/game/GameAdvance'
import { HomeBet, HomeBets } from './src/constants';

async  function initGame(homeBet: HomeBet, autoPlay: boolean){
	const game = new Game(homeBet, autoPlay)
	await game.initialize()
	await game.play()
}

(async () => {
	let readlineSync = require('readline-sync');
	let autoPlay = readlineSync.question("automatic play? [y/n]: ");
	autoPlay = autoPlay == "y"
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
	while(true){
		try{
			await initGame(homeBet, autoPlay)
		}catch(e){
			console.log(e)
		}
	}
})();
