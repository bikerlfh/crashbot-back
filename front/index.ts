import {URL_AVIATOR_DEMO, URL_BETPLAY} from "./src/constants";
import {Game} from './src/game/Game';
import {AviatorPage} from "./src/aviator/Aviator"
import {Control} from "./src/aviator/BetControl"

(async () => {
	const aviatorPage = new AviatorPage(URL_AVIATOR_DEMO, true)
	await aviatorPage.open()
	await aviatorPage.bet(5, 1.4, Control.Control2)
	// await aviatorPage._controls?.setAutoCashOut(2, Control.Control1)
	// await new_page.screenshot({ path: 'example.png' });
	// console.log("screenshot")
	//await browser.close();
  })();