import playwright from "playwright";
import {URL_AVIATOR_DEMO, URL_BETPLAY} from "./src/constants";
import {Game} from './src/game/Game';

(async () => {
	const browser = await playwright.chromium.launch({headless:false});
	const context = await browser.newContext();
	const page = await context.newPage();
	//page.on('domcontentloaded', (p) => console.log(`Loaded ${p.url()}`));
	await page.goto(URL_AVIATOR_DEMO);
	await page.getByRole('button', { name: 'Play Demo' }).click();
	await page.getByRole('button', { name: "Yes I’m over 18" }).click();
	await page.waitForTimeout(2000);
	let pages = context.pages();
	const page_game = pages[1]
	const multipiers: number[] = []
	let balance: number = 0
	let history_games
	// await page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", {timeout: 50000})
	while(true){
		try {
			await page_game.locator('.result-history').waitFor({
				timeout: 50000
			});
			break;
		} catch (e) {
			if (e instanceof playwright.errors.TimeoutError) {
				console.log("error timeout")
				return
			}
		}
	}
	history_games = await page_game.$('.result-history');
	console.log("result history found")
	// Get games history from tag app-payout-item
	if (history_games != null){
		let items = await history_games.$$('app-payout-item');
		items.slice().reverse().forEach(async (item) => {
			const multiplier = await item.textContent();
			if(multiplier !== null){
				const value = parseFloat(multiplier.replace(/\s/g, '').replace("x", ""))
				multipiers.push(value);
			}
		})
		await page.waitForTimeout(2000);
	}
	if(history_games == null){
		return
	}
	// bet controls
	const bet_controls = await page_game.$$("app-bet-control");
	const bet_control_1 = await bet_controls[0].$("app-navigation-switcher")
	const bet_control_2 = await bet_controls[1].$("app-navigation-switcher")
	const game = new Game("test", multipiers, null)
	console.log("last multiplier: " + multipiers[multipiers.length - 1])
	console.log("average 1:" + game.getAverage(1))
	console.log("average 2:" + game.getAverage(2))
	console.log("average 3:" + game.getAverage(3))
	while(true){
		try{
			const len_multipliers: number = multipiers.length - 1
			let locator =  await history_games.$('app-payout-item')
			if(locator == null){
				continue
			}
			const last_multiplier = parseFloat(await locator.textContent() || "0")
			if(last_multiplier == null){
				continue
			}
			if( multipiers[len_multipliers] != last_multiplier){
				multipiers.push(last_multiplier)
				game.addMultiplier(last_multiplier)
				const balance_element = await page_game.$(".balance>.amount");
				if(balance_element != null){
					balance = parseFloat(await balance_element.textContent() || "0")
				}
				console.log("changed " + last_multiplier + "; balance: " + balance)
				console.log("average 1:" + game.getAverage(1))
				console.log("average 2:" + game.getAverage(2))
				console.log("average 3:" + game.getAverage(3))
			}
		}
		catch (e) {
			if (e instanceof playwright.errors.TimeoutError) {
			console.log("error timeout")
			}
		}
	}
	// await new_page.screenshot({ path: 'example.png' });
	// console.log("screenshot")
	//await browser.close();
  })();