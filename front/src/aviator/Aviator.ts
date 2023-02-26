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
        this._controls = new BetControl(this._page);
        await this._controls.init()
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

}