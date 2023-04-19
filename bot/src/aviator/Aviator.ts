import playwright from "playwright";
import {BetControl, Control} from "./BetControl"
import { sleepNow } from "../game/utils";
import {sentLogToGUI, LogCode} from "../globals"


export class AviatorPage{
    _browser: playwright.Browser|null = null
    _context: playwright.BrowserContext|null = null
    _page: playwright.Page|null = null
    _appGame: playwright.Locator| null = null
    _historyGame: playwright.Locator|null = null
    _balanceElement: playwright.Locator|null = null
    _controls: BetControl|null = null
    minimumBet: number = 0
    maximumBet: number = 0
    maximumWinForOneBet: number = 0
    url: string
    multipliers: number[] = []
    balance: number

    constructor(url: string){
        this.url = url
        this.balance = 0
    }

    async _click(element: playwright.Locator){
        const box = await element.boundingBox();
        if(!box || !this._page){
            sentLogToGUI("page :: box or page does't exists", LogCode.ERROR)
            return
        }
        await this._page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, {steps: 50})
        await this._page.mouse.click(box.x + box.width / 2, box.y + box.height / 2, {delay: 50});
    }
    
    async _login(): Promise<void>{
        /* implement the login */
        return
    }

    async _getAppGame(): Promise<playwright.Locator>{
        if(!this._page ){
            throw "_getAppGame :: page is null"
        }
        
        let _appGame = null
        while(true){
            try {
                await this._page.locator("app-game").first().waitFor({ timeout: 50000 })
                _appGame = this._page.locator("app-game").first();
                // _appGame = this._page.locator("app-game").first()
                await _appGame.locator(".result-history").waitFor({
                    timeout: 50000
                });
                return _appGame
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    sentLogToGUI("page :: error timeout", LogCode.ERROR)
                    continue
                }
                throw e
            }
        }
    }

    async open(){
        this._browser = await playwright.chromium.launch({headless:false});
        this._context = await this._browser.newContext();
        this._page = await this._context.newPage();
        await this._page.goto(this.url, {timeout: 50000});
        await this._login()
        this._appGame = await this._getAppGame()
        this._historyGame = this._appGame.locator(".result-history");
        sentLogToGUI("result history found")
        await this.readBalance()
        await this.readMultipliers()
        // await this.readGameLimits()
        this._controls = new BetControl(this._appGame);
        await this._controls.init()
        sentLogToGUI("aviator loaded")
    }

    async close(){
        if(!this._page){
            return
        }
        await this._page.close()
        await this._browser?.close()
        // TODO: implment close session of home bet
    }
    
    async readGameLimits(){
        if(this._appGame == null || this._page == null){
            throw "readGameLimits :: _appGame is null"
        }
        const menu = this._appGame.locator(".dropdown-toggle.user")
        if(menu == null){
            throw "readGameLimits :: menu is null"
        }
        await menu.click()
        await this._page.waitForTimeout(400);
        // app-settings-menu
        // app-user-menu-dropdown
        const appUserMenu = this._appGame.locator("app-settings-menu")
        if(appUserMenu == null){
            throw "readGameLimits :: appusermenu is null"
        }
        const listMenu = appUserMenu.locator(".list-menu").last()
        const menuLimits = listMenu.locator(".list-menu-item").last()
        await menuLimits.click()
        await this._page.waitForTimeout(400);
        const limits = await this._page.locator("app-game-limits ul>li>span").all()
        this.minimumBet = parseFloat((await limits[0].textContent())?.split(" ")[0] || "0")
        this.maximumBet = parseFloat((await limits[1].textContent())?.split(" ")[0] || "0")
        this.maximumWinForOneBet =  parseFloat((await limits[2].textContent())?.split(" ")[0] || "0")
        const buttonClose = this._page.locator("ngb-modal-window")
        await buttonClose.click()
        sentLogToGUI(`minimumBet: ${this.minimumBet}`)
        sentLogToGUI(`maximumBet: ${this.maximumBet}`)
        sentLogToGUI(`maximumWinForOneBet: ${this.maximumWinForOneBet}`)
        
    }

    async readBalance(): Promise<number | null>{
        if(this._appGame == null){
            throw "readBalance :: _appGame is null"
        }
        this._balanceElement = this._appGame.locator(".balance>div>.amount")
        if(this._balanceElement == null){
            throw "balance element is null"
        }
        this.balance = parseFloat(await this._balanceElement.textContent() || "0")
        sentLogToGUI(`balance: ${this.balance}`)
        return this.balance
    }

    _formatMultiplier(multiplier: string): number{
        return parseFloat(multiplier.replace(/\s/g, '').replace("x", ""))
    }

    async readMultipliers(){
        if (!this._page || !this._historyGame){
            throw "readMultipliers :: the page or the history game not exists"
        }
        // app-bubble-multiplier
        // app-payout-item
        let items = await this._historyGame.locator('app-bubble-multiplier.payout.ng-star-inserted').all();
        items.reverse().forEach(async (item) => {
            const multiplier = await item.textContent();
            if(multiplier !== null){
                // const value = this._formatMultiplier(multiplier)
                this.multipliers.push(this._formatMultiplier(multiplier));
            }
        })
        await this._page.waitForTimeout(2000);
        //sentLogToGUI("multiplier aviator:", this.multipliers)
    }

    async bet(amount: number, multiplier: number, control: Control){
        if(this._controls == null){
            throw "AviatorPage :: no _controls"
        }
        this._controls.bet(amount, multiplier, control)
    }

    async waitNextGame(){
        if(this._historyGame == null){
            throw "waitNextGame :: no historyGame"
        }
        const lastMultiplierSaved = this.multipliers.slice(-1)[0]
        let lastMultiplierContent = null
        let locator = null
        let lastMultiplier = null
        await this._historyGame.locator('app-bubble-multiplier').first().waitFor({timeout: 1000})    
        do{
            locator = this._historyGame.locator('app-bubble-multiplier').first()
            lastMultiplierContent = await locator.textContent({timeout:1000})
            lastMultiplier = lastMultiplierContent? this._formatMultiplier(lastMultiplierContent): lastMultiplierSaved;
            if(lastMultiplierSaved != lastMultiplier){
                this.multipliers.push(lastMultiplier)
                sentLogToGUI(`New multiplier: ${lastMultiplier}`)
                this.multipliers = this.multipliers.slice(1)
                return
            }
            await sleepNow(200)
        } while(true);
    }
}