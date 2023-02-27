import playwright from "playwright";

export enum Control{
    Control1=1,
    Control2=2
}

export class BetControl{
    aviatorPage: playwright.Page
    _betControl_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _betControl_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _amountInput_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _amountInput_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _betSwitcherButton_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoSwitcherButton_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _betSwitcherButton_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoSwitcherButton_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoCashOutSwitcher_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoCashOutSwitcher_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoCashOutMultiplier_1: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _autoCashOutMultiplier_2: playwright.ElementHandle<SVGElement|HTMLElement>|null = null
    _betButton_1: playwright.Locator|null = null
    _betButton_2: playwright.Locator|null = null

    isActiveAutoCashOutControl_1: boolean = false
    isActiveAutoCashOutControl_2: boolean = false
    wasLoad: boolean

    constructor(aviatorPage: playwright.Page){
        this.aviatorPage = aviatorPage
        this.wasLoad = false
    }

    _randomDelay() {
        const min = 15
        const max = 50
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    async init(){
        const bet_controls = await this.aviatorPage.$$("app-bet-control");
        // app-navigation-switcher
	    this._betControl_1 = bet_controls[0]
	    this._betControl_2 = bet_controls[1]
        if(this._betControl_1 == null || this._betControl_2 == null){
            console.log("no bet controls")
            return
        }
        const inputAppSpinner_1 = await this._betControl_1.$("app-spinner")
        const inputAppSpinner_2 = await this._betControl_2.$("app-spinner")
        if(inputAppSpinner_1 == null || inputAppSpinner_2 == null){
            console.log("no inputAppSpinner_1 or inputAppSpinner_2")
            return
        }
        this._amountInput_1 = await inputAppSpinner_1.$("input")
        this._amountInput_2 = await inputAppSpinner_2.$("input")
        const appNavigationSwitcher_1 = await this._betControl_1.$("app-navigation-switcher")
        const appNavigationSwitcher_2 = await this._betControl_2.$("app-navigation-switcher")
        if(appNavigationSwitcher_1 == null){
            console.log("no appNavigationSwitcher_1")
            return
        }
        if(appNavigationSwitcher_2 == null){
            console.log("no appNavigationSwitcher_2")
            return
        }
        const buttons_1 = await appNavigationSwitcher_1.$$("button")
        const buttons_2 = await appNavigationSwitcher_2.$$("button")
        this._betSwitcherButton_1 = buttons_1[0]
        this._autoSwitcherButton_1 = buttons_1[1]
        this._betSwitcherButton_2 = buttons_2[0]
        this._autoSwitcherButton_2 = buttons_2[1]
        this._autoCashOutSwitcher_1 = await this._betControl_1.$("app-ui-switcher")
        this._autoCashOutSwitcher_2 = await this._betControl_2.$("app-ui-switcher")
        await this._autoSwitcherButton_1.click({delay: this._randomDelay()})
        await this._autoSwitcherButton_2.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_1?.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_2?.click({delay: this._randomDelay()})
        const cashOutSpinner_1 = await this._betControl_1.$(".cashout-spinner-wrapper")
        const cachOutSpinner_2 = await this._betControl_2.$(".cashout-spinner-wrapper")
        if(cashOutSpinner_1 == null){
            console.log("no cashOutSpinner_1")
            return
        }
        if(cachOutSpinner_2 == null){
            console.log("no cachOutSpinner_2")
            return
        }
        this._autoCashOutMultiplier_1 = await cashOutSpinner_1.$("input") 
        this._autoCashOutMultiplier_2 = await cachOutSpinner_2.$("input") 
        
        // this._betButton_1 = await this._betControl_1.$(".buttons-block>button")
        //this._betButton_2 = await this._betControl_2.$(".buttons-block>button")
        // app-bet-control.buttons-block>button
        const betButtons = this.aviatorPage.locator("button", {hasText: /\B\E\T/})
        this._betButton_1 = betButtons.first()
        this._betButton_2 = betButtons.last()
        this.wasLoad = true
    }

    async setAutoCashOut(multiplier: number, control:Control){
        console.log("setAutoCashOut control: ", control)
        let autoCashOutMultiplier = this._autoCashOutMultiplier_1
        if(control == Control.Control2){
            autoCashOutMultiplier = this._autoCashOutMultiplier_2
        }
        if(autoCashOutMultiplier == null){
            console.log("buttons null autoCashOutMultiplier")
            return
        }
        await autoCashOutMultiplier.fill("")
        await this.aviatorPage.waitForTimeout(500);
        await autoCashOutMultiplier.type(multiplier.toString(), {delay: this._randomDelay()})
        await this.aviatorPage.waitForTimeout(500);
    }
    
    async updateAmount(amount: number, control:Control){
        let input = this._amountInput_1
        if(control == Control.Control2){
            input = this._amountInput_2
        }
        if(input == null){
            console.log("updateAmount :: input null")
            return
        }
        await input.fill("")
        await input.type(amount.toString(), {delay: this._randomDelay()})
    }

    async bet(
        amount: number,
        multiplier: number,
        control:Control, 
    ){
        await this.setAutoCashOut(multiplier, control)
        await this.updateAmount(amount, control)
        if(this._betButton_1 == null || this._betButton_2 == null){
            console.log("bet: bet button null. control: ", control)
            return
        }
        if(control === Control.Control1){
            await this._betButton_1.click();({delay: this._randomDelay()})
            return
        }
        await this._betButton_2.click({delay: this._randomDelay()})
        await this.aviatorPage.waitForTimeout(1000)
    }
}