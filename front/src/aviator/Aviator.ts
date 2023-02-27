import playwright from "playwright";
import {BetControl, Control} from "./BetControl"

export class AviatorPage{
    _browser: playwright.Browser|null = null
    _context: playwright.BrowserContext|null = null
    _page: playwright.Page|null = null
    _historyGame: playwright.ElementHandle<SVGElement | HTMLElement>|null = null
    _balanceElement: playwright.ElementHandle<SVGElement | HTMLElement>|null = null
    _controls: BetControl|null = null
    isDemo: boolean = false
    minimumBet: number = 0
    maximumBet: number = 0
    maximumWinForOneBet: number = 0
    url: string
    multipliers: number[] = []
    balance: number

    constructor(url: string, isDemo: boolean){
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
                await this._page.locator('.result-history').waitFor({
                    timeout: 50000
                });
                break;
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    console.log("error timeout")
                    continue
                }
                return
            }
        }
        this._historyGame = await this._page.$('.result-history');
        console.log("result history found")
        await this.readBalance()
        await this.readMultipliers()
        await this.readGameLimits()
        this._controls = new BetControl(this._page);
        await this._controls.init()
    }
    
    async readGameLimits(){
        if(this._page == null){
            return
        }
        const menu = await this._page.$(".dropdown-toggle.user")
        if(menu == null){
            return
        }
        await menu.click()
        await this._page.waitForTimeout(1000);
        const appUserMenu = await this._page.$("app-user-menu-dropdown")
        if(appUserMenu == null){
            console.log("appusermenu is null")
            return
        }
        const listMenu = (await appUserMenu.$$(".list-menu")).slice(-1)[0]
        const menuLimits = (await listMenu.$$(".list-menu-item")).slice(-1)[0]
        await menuLimits.click()
        await this._page.waitForTimeout(1000);
        const limits = await this._page.$$("app-game-limits ul>li>span")
        this.minimumBet = parseFloat((await limits[0].textContent())?.split(" ")[0] || "0")
        this.maximumBet = parseFloat((await limits[1].textContent())?.split(" ")[0] || "0")
        this.maximumWinForOneBet =  parseFloat((await limits[2].textContent())?.split(" ")[0] || "0")
        console.log("minimumBet: ", this.minimumBet)
        console.log("maximumBet: ", this.maximumBet)
        console.log("maximumWinForOneBet: ", this.maximumWinForOneBet)
    }

    async readBalance(): Promise<number | null>{
        if(this._page == null){
            console.log("readBalance :: page is null")
            return null
        }
        this._balanceElement = await this._page.$(".balance>.amount");
        if(this._balanceElement != null){
            this.balance = parseFloat(await this._balanceElement.textContent() || "0")
            console.log("balance: ", this.balance)
        }
        return this.balance
    }

    async readMultipliers(){
        if (this._page && this._historyGame){
            let items = await this._historyGame.$$('app-payout-item');
            items.slice().reverse().forEach(async (item) => {
                const multiplier = await item.textContent();
                if(multiplier !== null){
                    const value = parseFloat(multiplier.replace(/\s/g, '').replace("x", ""))
                    this.multipliers.push(value);
                }
            })
            await this._page.waitForTimeout(2000);
        }
    }

    async bet(amount: number, multiplier: number, control: Control){
        if(this._controls == null){
            console.log("AviatorPage :: no _controls")
            return
        }
        this._controls.bet(amount, control, true, multiplier)
    }

    async waitNextGame(){
        if(this._historyGame == null){
            throw "waitNextGame :: no historyGame"
        }
        while(true){
            try{
                const len_multipliers: number = this.multipliers.length - 1
                let locator =  await this._historyGame.$('app-payout-item')
                if(locator == null){
                    continue
                }
                const last_multiplier = parseFloat(await locator.textContent() || "0")
                if(last_multiplier == null){
                    continue
                }
                if(this.multipliers[len_multipliers] != last_multiplier){
                    this.multipliers.push(last_multiplier)
                    console.log("last multiplier", last_multiplier)
                    return
                }
            }
            catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                console.log("error timeout")
                }
            }
        }
    }

}