import playwright from "playwright";
import {BetControl, Control} from "./BetControl"

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
            console.log("_click :: box or page does't exists")
            return
        }
        // await this._page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, {steps: 5})
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
        while(true){
            try {
                // this._appGame = this._page.locator("app-game").first()
                const _appGame = this._page.locator("app-game").first()
                await _appGame.locator(".result-history").waitFor({
                    timeout: 30000
                });
                return _appGame
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    console.log("error timeout")
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
        await this._page.goto(this.url);
        await this._login()
        this._appGame = await this._getAppGame()
        this._historyGame = this._appGame.locator(".result-history");
        console.log("result history found")
        await this.readBalance()
        await this.readMultipliers()
        // await this.readGameLimits()
        this._controls = new BetControl(this._appGame);
        await this._controls.init()
        console.log("aviator loaded")
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
        console.log("minimumBet: ", this.minimumBet)
        console.log("maximumBet: ", this.maximumBet)
        console.log("maximumWinForOneBet: ", this.maximumWinForOneBet)
        
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
        console.log("balance: ", this.balance)
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
        let items = await this._historyGame.locator('app-bubble-multiplier').all();
        items.slice().reverse().forEach(async (item) => {
            const multiplier = await item.textContent();
            if(multiplier !== null){
                const value = this._formatMultiplier(multiplier)
                this.multipliers.push(value);
            }
        })
        await this._page.waitForTimeout(2000);
        console.log("multiplier:", this.multipliers)
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
        while(true){
            try{
                const len_multipliers: number = this.multipliers.length - 1
                let locator = this._historyGame.locator('app-bubble-multiplier').first()
                if(locator == null){
                    continue
                }
                let lastMultiplierContent = await locator.textContent({timeout:1000})
                if(!lastMultiplierContent){
                    console.log("waitNextGame :: lastMultiplierContent not exists")
                    continue
                }
                const lastMultiplier = this._formatMultiplier(lastMultiplierContent)
                if(this.multipliers[len_multipliers] != lastMultiplier){
                    this.multipliers.push(lastMultiplier)
                    console.log("waitNextGame :: new multiplier:", lastMultiplier)
                    return
                }
            }
            catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    console.log("waitNextGame :: error timeout")
                }
            }
        }
    }

}