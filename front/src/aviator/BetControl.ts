import playwright from "playwright";
import { mainModule } from "process";

export enum Control{
    Control1=1,
    Control2=2
}

export class BetControl{
    aviatorPage: playwright.Locator
    _betControl_1: playwright.Locator|null = null
    _betControl_2: playwright.Locator|null = null
    _amountInput_1: playwright.Locator|null = null
    _amountInput_2: playwright.Locator|null = null
    _betSwitcherButton_1: playwright.Locator|null = null
    _autoSwitcherButton_1: playwright.Locator|null = null
    _betSwitcherButton_2: playwright.Locator|null = null
    _autoSwitcherButton_2: playwright.Locator|null = null
    _autoCashOutSwitcher_1: playwright.Locator|null = null
    _autoCashOutSwitcher_2: playwright.Locator|null = null
    _autoCashOutMultiplier_1: playwright.Locator|null = null
    _autoCashOutMultiplier_2: playwright.Locator|null = null
    _betButton_1: playwright.Locator|null = null
    _betButton_2: playwright.Locator|null = null

    isActiveAutoCashOutControl_1: boolean = false
    isActiveAutoCashOutControl_2: boolean = false
    wasLoad: boolean

    constructor(aviatorPage: playwright.Locator){
        this.aviatorPage = aviatorPage
        this.wasLoad = false
    }

    _randomDelay() {
        const min = 15
        const max = 50
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    async init(){
        const bet_controls = this.aviatorPage.locator("app-bet-control");
        // app-navigation-switcher
	    this._betControl_1 = bet_controls.first()
	    this._betControl_2 = bet_controls.last()
        if(this._betControl_1 == null || this._betControl_2 == null){
            throw "no bet controls"
        }
        const inputAppSpinner_1 = this._betControl_1.locator("app-spinner").first()
        const inputAppSpinner_2 = this._betControl_2.locator("app-spinner").first()
        if(inputAppSpinner_1 == null || inputAppSpinner_2 == null){
            throw "no inputAppSpinner_1 or inputAppSpinner_2"
        }
        this._amountInput_1 = inputAppSpinner_1.locator("input").first()
        this._amountInput_2 = inputAppSpinner_2.locator("input").first()
        const appNavigationSwitcher_1 = this._betControl_1.locator("app-navigation-switcher").first()
        const appNavigationSwitcher_2 = this._betControl_2.locator("app-navigation-switcher").first()
        if(appNavigationSwitcher_1 == null){
            throw "no appNavigationSwitcher_1"
        }
        if(appNavigationSwitcher_2 == null){
            throw "no appNavigationSwitcher_2"
        }
        const buttons_1 = appNavigationSwitcher_1.locator("button")
        const buttons_2 = appNavigationSwitcher_2.locator("button")
        this._betSwitcherButton_1 = buttons_1.first()
        this._autoSwitcherButton_1 = buttons_1.last()
        this._betSwitcherButton_2 = buttons_2.first()
        this._autoSwitcherButton_2 = buttons_2.last()
        this._autoCashOutSwitcher_1 = this._betControl_1.locator("app-ui-switcher").first()
        this._autoCashOutSwitcher_2 = this._betControl_2.locator("app-ui-switcher").first()
        await this._autoSwitcherButton_1.click({delay: this._randomDelay()})
        await this._autoSwitcherButton_2.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_1?.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_2?.click({delay: this._randomDelay()})
        const cashOutSpinner_1 = this._betControl_1.locator(".cashout-spinner-wrapper").first()
        const cachOutSpinner_2 = this._betControl_2.locator(".cashout-spinner-wrapper").first()
        if(cashOutSpinner_1 == null){
            throw "no cashOutSpinner_1"
        }
        if(cachOutSpinner_2 == null){
            throw "no cachOutSpinner_2"
        }
        this._autoCashOutMultiplier_1 = cashOutSpinner_1.locator("input").first()
        this._autoCashOutMultiplier_2 = cachOutSpinner_2.locator("input").first()
        if(!this._autoCashOutMultiplier_1){
            throw "no _autoCashOutMultiplier_1"
        }
        if(!this._autoCashOutMultiplier_2){
            throw "no _autoCashOutMultiplier_2"
        }
        // app-bet-control.buttons-block>button
        // const betButtons = this.aviatorPage.locator("button", {hasText: /\B\E\T/})
        const betButtons = this.aviatorPage.locator("button.bet")
        this._betButton_1 = betButtons.first()
        this._betButton_2 = betButtons.last()
        this.wasLoad = true
    }

    async setAutoCashOut(multiplier: number, control:Control){
        let autoCashOutMultiplier = this._autoCashOutMultiplier_1
        if(control === Control.Control2){
            autoCashOutMultiplier = this._autoCashOutMultiplier_2
        }
        if(!autoCashOutMultiplier){
            throw "buttons null autoCashOutMultiplier"
        }
        const value = parseFloat(parseFloat(await autoCashOutMultiplier.inputValue({timeout: 500})).toFixed(0))
        if(value != multiplier){
            await autoCashOutMultiplier.fill("", {timeout: 500})
            await autoCashOutMultiplier.type(multiplier.toString(), {delay: 100})
        }
    }
    
    async updateAmount(amount: number, control:Control){
        let input = this._amountInput_1
        if(control == Control.Control2){
            input = this._amountInput_2
        }
        if(input == null){
            throw "updateAmount :: input null"
        }
        const value = parseFloat(parseFloat(await input.inputValue({timeout: 500})).toFixed(0))
        if(value != amount){
            await input.fill("", {timeout: 500})
            await input.type(amount.toString(), {delay: 100})
        }
       // await this.aviatorPage.waitForTimeout(500);
    }

    async bet(
        amount: number,
        multiplier: number,
        control: Control, 
    ){
        if(multiplier == null || amount == null){
            throw "bet :: no multiplier or amount"
        }
        await this.setAutoCashOut(multiplier, control)
        await this.updateAmount(amount, control)
        if(this._betButton_1 == null || this._betButton_2 == null){
            throw "bet: bet button null. control"
        }
        if(control === Control.Control1){
            await this._betButton_1.click();({delay: this._randomDelay()})
            //await this.aviatorPage.waitForTimeout(1000)
            return
        }
        await this._betButton_2.click({delay: this._randomDelay()})
        //await this.aviatorPage.waitForTimeout(1000)
    }
}