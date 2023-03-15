import * as dotenv from 'dotenv';
dotenv.config()
import {Game} from './src/game/Game'
import { AviatorBetPlay } from "./src/aviator/AviatorBetPlay"
import { AviatorDemo } from "./src/aviator/AviatorDemo"
import { AviatorOneWin } from "./src/aviator/AviatorOneWin"
import { HomeBets } from './src/constants';
import { Control } from './src/aviator/BetControl';
import { AviatorBotAPI } from './src/api/AviatorBotAPI';


(async () => {
	// const predictions = await AviatorBotAPI.requestPrediction(HomeBets.betplay.id)
	//console.log(predictions)
	const homeBet = HomeBets.betplay
	const aviatorPage = new AviatorBetPlay()
	await aviatorPage.open()
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
			for (let index = 0; index < bets.length; index++) {
				const bet = bets[index];
				const control = index == 0? Control.Control1: Control.Control2
				await aviatorPage.bet(bet.amount, bet.multiplier, control)
				await sleepNow(2000)
			}
		}
	}
	// const average = game.getAverage(1)
	// await aviatorPage.bet(5, average, Control.Control2)
	// await aviatorPage._controls?.setAutoCashOut(2, Control.Control1)
	// await new_page.screenshot({ path: 'example.png' });
	// console.log("screenshot")
	// await browser.close();
  })();
