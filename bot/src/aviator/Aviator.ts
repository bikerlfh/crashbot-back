import playwright from "playwright";
import {BetControl, Control} from "./BetControl"
import { sleepNow } from "../game/utils";
import {sendEventToGUI} from "../ws/gui_events"


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
            sendEventToGUI.log.error("page :: box or page does't exists")
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
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "_getAppGame :: page is null"
            })
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
                    sendEventToGUI.log.debug("page :: error timeout")
                    continue
                }
                sendEventToGUI.exception({
                    location: "AviatorPage",
                    message: `_getAppGame :: ${e}`
                })
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
        sendEventToGUI.log.debug("Result history found")
        await this.readBalance()
        await this.readMultipliers()
        // await this.readGameLimits()
        this._controls = new BetControl(this._appGame);
        await this._controls.init()
        sendEventToGUI.log.success("Aviator loaded")
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
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readGameLimits :: _appGame or _page is null"
            })
            throw "readGameLimits :: _appGame is null"
        }
        const menu = this._appGame.locator(".dropdown-toggle.user")
        if(menu == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readGameLimits :: menu is null"
            })
            throw "readGameLimits :: menu is null"
        }
        await menu.click()
        await this._page.waitForTimeout(400);
        // app-settings-menu
        // app-user-menu-dropdown
        const appUserMenu = this._appGame.locator("app-settings-menu")
        if(appUserMenu == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readGameLimits :: appusermenu is null"
            })
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
        sendEventToGUI.log.debug(`minimumBet: ${this.minimumBet}`)
        sendEventToGUI.log.debug(`maximumBet: ${this.maximumBet}`)
        sendEventToGUI.log.debug(`maximumWinForOneBet: ${this.maximumWinForOneBet}`)
        
    }

    async readBalance(): Promise<number | null>{
        if(this._appGame == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readBalance :: _appGame is null"
            })
            throw "readBalance :: _appGame is null"
        }
        this._balanceElement = this._appGame.locator(".balance>div>.amount")
        if(this._balanceElement == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readBalance :: balance element is null"
            })
            throw "balance element is null"
        }
        this.balance = parseFloat(await this._balanceElement.textContent() || "0")
        return this.balance
    }

    _formatMultiplier(multiplier: string): number{
        return parseFloat(multiplier.replace(/\s/g, '').replace("x", ""))
    }

    async readMultipliers(){
        if (!this._page || !this._historyGame){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "readMultipliers :: the page or the history game not exists"
            })
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
        //sendLogToGUI("multiplier aviator:", this.multipliers)
    }

    async bet(amount: number, multiplier: number, control: Control){
        if(this._controls == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "AviatorPage :: no _controls"
            })
            throw "AviatorPage :: no _controls"
        }
        this._controls.bet(amount, multiplier, control)
    }

    async waitNextGame(){
        if(this._historyGame == null){
            sendEventToGUI.exception({
                location: "AviatorPage",
                message: "waitNextGame :: no historyGame"
            })
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
                sendEventToGUI.log.success(`New Multiplier: ${lastMultiplier}`)
                this.multipliers = this.multipliers.slice(1)
                return
            }
            await sleepNow(200)
        } while(true);
    }
}