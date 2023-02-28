import {URL_AVIATOR_DEMO, URL_BETPLAY} from "./src/constants";
import {Game} from './src/game/Game';
import {AviatorPage} from "./src/aviator/Aviator"
import {Control} from "./src/aviator/BetControl"

(async () => {
	const aviatorPage = new AviatorPage(URL_AVIATOR_DEMO, true)
	await aviatorPage.open()
	const game = new Game(
		"demo", 
		aviatorPage.multipliers,
		aviatorPage.balance, 
		aviatorPage.minimumBet,
		aviatorPage.maximumBet,
		aviatorPage.maximumWinForOneBet
	)
	while(true){
		await aviatorPage.waitNextGame()
		game.addMultiplier(aviatorPage.multipliers.slice(-1)[0])
		const bets = game.getNextBet()
		if(bets.length){
			console.log("bets:", bets)
			for (let index = 0; index < bets.length; index++) {
				const bet = bets[index];
				const control = index == 0? Control.Control2: Control.Control1
				await aviatorPage.bet(bet.amount, bet.multiplier, control)
			}
			/*const bet = bets[0];
			await aviatorPage.bet(bet.amount, bet.multiplier, Control.Control1)*/
		}
	}
	// const average = game.getAverage(1)
	// await aviatorPage.bet(5, average, Control.Control2)
	// await aviatorPage._controls?.setAutoCashOut(2, Control.Control1)
	// await new_page.screenshot({ path: 'example.png' });
	// console.log("screenshot")
	// await browser.close();
  })();