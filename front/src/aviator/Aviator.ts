import { loadavg } from "os";
import playwright from "playwright";
import {BetControl, Control} from "./BetControl"

export class AviatorPage{
    _browser: playwright.Browser|null = null
    _context: playwright.BrowserContext|null = null
    _page: playwright.Page|null = null
    _historyGame: playwright.Locator|null = null
    _balanceElement: playwright.ElementHandle<SVGElement | HTMLElement>|null = null
    _controls: BetControl|null = null
    isDemo: boolean = false
    minimumBet: number = 0
    maximumBet: number = 0
    maximumWinForOneBet: number = 0
    url: string
    multipliers: number[] = []
    balance: number

    constructor(url: string, isDemo: boolean = false){
        this.url = url
        this.isDemo = isDemo
        this.balance = 0
    }

    async open(){
        this._browser = await playwright.chromium.launch({headless:false});
        this._context = await this._browser.newContext();
        this._page = await this._context.newPage();
        await this._page.goto(this.url);
        if(this.isDemo){
            await this._page.getByRole('button', { name: 'Play Demo' }).click();
	        await this._page.getByRole('button', { name: "Yes I’m over 18" }).click();
	        await this._page.waitForTimeout(2000);
            let pages = this._context.pages();
	        this._page =pages[1]
        }
        while(true){
            try {
                
                await this._page.locator(".result-history").waitFor({
                    timeout: 30000
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
        this._historyGame = this._page.locator(".result-history");
        console.log("result history found")
        this._controls = new BetControl(this._page.locator("body"));
        await this._controls.init()
        await this.readBalance()
        await this.readMultipliers()
        await this.readGameLimits()
        console.log("aviator loaded")
    }
    
    async readGameLimits(){
        if(this._page == null){
            throw "no page"
        }
        const menu = await this._page.$(".dropdown-toggle.user")
        if(menu == null){
            throw "no menu"
        }
        await menu.click()
        await this._page.waitForTimeout(400);
        // app-settings-menu
        // app-user-menu-dropdown
        const appUserMenu = await this._page.$("app-settings-menu")
        if(appUserMenu == null){
            throw "appusermenu is null"
        }
        const listMenu = (await appUserMenu.$$(".list-menu")).slice(-1)[0]
        const menuLimits = (await listMenu.$$(".list-menu-item")).slice(-1)[0]
        await menuLimits.click()
        await this._page.waitForTimeout(400);
        const limits = await this._page.$$("app-game-limits ul>li>span")
        this.minimumBet = parseFloat((await limits[0].textContent())?.split(" ")[0] || "0")
        this.maximumBet = parseFloat((await limits[1].textContent())?.split(" ")[0] || "0")
        this.maximumWinForOneBet =  parseFloat((await limits[2].textContent())?.split(" ")[0] || "0")
        const buttonClose = await this._page.$("ngb-modal-window")
        await buttonClose?.click()
        console.log("minimumBet: ", this.minimumBet)
        console.log("maximumBet: ", this.maximumBet)
        console.log("maximumWinForOneBet: ", this.maximumWinForOneBet)
        
    }

    async readBalance(): Promise<number | null>{
        if(this._page == null){
            throw "readBalance :: page is null"
        }
        this._balanceElement = await this._page.$(".balance>div>.amount");
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
        if (this._page && this._historyGame){
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
        }
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