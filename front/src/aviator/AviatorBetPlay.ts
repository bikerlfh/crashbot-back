import playwright from 'playwright'
import {AviatorPage} from './Aviator'
import {BetControl} from "./BetControl"


export class AviatorBetPlay extends AviatorPage{

    async open(){
        this._browser = await playwright.chromium.launch({headless:false});
        this._context = await this._browser.newContext();
        this._page = await this._context.newPage();
        await this._page.goto(this.url);
        await this._page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", {timeout: 50000})
        let _frame = null
        let main = null
        while(true){
            try {
                // gameFrame
                // spribe-game
                _frame = this._page.frameLocator("#gameFrame").frameLocator("#spribe-game")
                main = _frame.locator("app-game").first()
                await main.locator(".result-history").waitFor({
                    timeout: 5000
                });
                break;
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    console.log("error timeout")
                    continue
                }
                throw e
            }
        }
        this._historyGame = main.locator(".result-history");
        console.log("result history found")
        this._controls = new BetControl(main);
        await this._controls.init()
        await this.readBalance()
        await this.readMultipliers()
        await this.readGameLimits()
        console.log("aviator loaded")
    }

}