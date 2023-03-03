import * as dotenv from 'dotenv';
dotenv.config()
import {Game} from './src/game/Game'
// import {AviatorPage} from "./src/aviator/Aviator"
import { AviatorBetPlay } from "./src/aviator/AviatorBetPlay"
import { AviatorDemo } from "./src/aviator/AviatorDemo"
import { AviatorOneWin } from "./src/aviator/AviatorOneWin"


(async () => {
	const aviatorPage = new AviatorOneWin()
	await aviatorPage.open()
	const game = new Game(
		"demo", 
		aviatorPage.multipliers,
		aviatorPage.balance, 
		aviatorPage.minimumBet,
		aviatorPage.maximumBet,
		aviatorPage.maximumWinForOneBet
	)
	const sleepNow = (delay: number) => new Promise((resolve) =>setTimeout(resolve, delay))
	while(true){
		await aviatorPage.waitNextGame()
		game.addMultiplier(aviatorPage.multipliers.slice(-1)[0])
		const bets = game.getNextBet()
		if(bets.length){
			console.log("bets:", bets)
			/*for (let index = 0; index < bets.length; index++) {
				const bet = bets[index];
				const control = index == 0? Control.Control1: Control.Control2
				await aviatorPage.bet(bet.amount, bet.multiplier, control)
				await sleepNow(2000)
			}
			*/
		
		}
	}
	// const average = game.getAverage(1)
	// await aviatorPage.bet(5, average, Control.Control2)
	// await aviatorPage._controls?.setAutoCashOut(2, Control.Control1)
	// await new_page.screenshot({ path: 'example.png' });
	// console.log("screenshot")
	// await browser.close();
  })();