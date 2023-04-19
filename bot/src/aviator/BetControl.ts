import playwright from "playwright";
import { roundNumber } from "../game/utils";
import {sendLogToGUI, LogCode} from "../globals"

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
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no bet controls"
            }, LogCode.EXCEPTION)
            throw "no bet controls"
        }
        const inputAppSpinner_1 = this._betControl_1.locator(".bet-block>app-spinner").first()
        const inputAppSpinner_2 = this._betControl_2.locator(".bet-block>app-spinner").first()
        if(inputAppSpinner_1 == null || inputAppSpinner_2 == null){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no inputAppSpinner_1 or inputAppSpinner_2"
            }, LogCode.EXCEPTION)
            throw "no inputAppSpinner_1 or inputAppSpinner_2"
        }
        this._amountInput_1 = inputAppSpinner_1.locator("input").first()
        this._amountInput_2 = inputAppSpinner_2.locator("input").first()
        const buttonsSwitcher_1 = await this._betControl_1.locator("app-navigation-switcher>div>button").all()
        const buttonsSwitcher_2 = await this._betControl_2.locator("app-navigation-switcher>div>button").all()
        if(!buttonsSwitcher_1){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no buttonsSwitcher_1"
            }, LogCode.EXCEPTION)
            throw "no buttonsSwitcher_1"
        }
        if(!buttonsSwitcher_2){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no buttonsSwitcher_2"
            }, LogCode.EXCEPTION)
            throw "no buttonsSwitcher_2"
        }
        this._betSwitcherButton_1 = buttonsSwitcher_1[0]
        this._autoSwitcherButton_1 = buttonsSwitcher_1[1]
        this._betSwitcherButton_2 = buttonsSwitcher_2[0]
        this._autoSwitcherButton_2 = buttonsSwitcher_2[1]
        this._autoCashOutSwitcher_1 = this._betControl_1.locator("app-ui-switcher").last()
        this._autoCashOutSwitcher_2 = this._betControl_2.locator("app-ui-switcher").last()
        await this._autoSwitcherButton_1.click({delay: this._randomDelay()})
        await this._autoSwitcherButton_2.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_1.click({delay: this._randomDelay()})
        await this._autoCashOutSwitcher_2.click({delay: this._randomDelay()})
        const cashOutSpinner_1 = this._betControl_1.locator(".cashout-spinner-wrapper").first()
        const cachOutSpinner_2 = this._betControl_2.locator(".cashout-spinner-wrapper").first()
        if(cashOutSpinner_1 == null){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no cashOutSpinner_1"
            }, LogCode.EXCEPTION)
            throw "no cashOutSpinner_1"
        }
        if(cachOutSpinner_2 == null){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no cachOutSpinner_2"
            }, LogCode.EXCEPTION)
            throw "no cachOutSpinner_2"
        }
        this._autoCashOutMultiplier_1 = cashOutSpinner_1.locator("input").first()
        this._autoCashOutMultiplier_2 = cachOutSpinner_2.locator("input").first()
        if(!this._autoCashOutMultiplier_1){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no _autoCashOutMultiplier_1"
            }, LogCode.EXCEPTION)
            throw "no _autoCashOutMultiplier_1"
        }
        if(!this._autoCashOutMultiplier_2){
            sendLogToGUI({
                location: "BetControl",
                message: "init :: no _autoCashOutMultiplier_2"
            }, LogCode.EXCEPTION)
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
            sendLogToGUI({
                location: "BetControl",
                message: "setAutoCashOut :: buttons null autoCashOutMultiplier"
            }, LogCode.EXCEPTION)
            throw "buttons null autoCashOutMultiplier"
        }
        const value = roundNumber(parseFloat(await autoCashOutMultiplier.inputValue({timeout: 1000})), 2)
        if(value != multiplier){
            await autoCashOutMultiplier.fill("", {timeout: 1000})
            await autoCashOutMultiplier.type(multiplier.toString(), {delay: 100})
        }
        //await autoCashOutMultiplier.fill("", {timeout: 500})
        //await autoCashOutMultiplier.type(multiplier.toString(), {delay: 100})
    }
    
    async updateAmount(amount: number, control:Control){
        let input = this._amountInput_1
        if(control == Control.Control2){
            input = this._amountInput_2
        }
        if(input == null){
            sendLogToGUI({
                location: "BetControl",
                message: "updateAmount :: input null"
            }, LogCode.EXCEPTION)
            throw "updateAmount :: input null"
        }
        const value = roundNumber(parseFloat(await input.inputValue({timeout: 1000})), 0)
        if(value != amount){
            await input.fill("", {timeout: 1000})
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
            sendLogToGUI({
                location: "BetControl",
                message: "bet :: no multiplier or amount"
            }, LogCode.EXCEPTION)
            throw "bet :: no multiplier or amount"
        }
        await this.setAutoCashOut(multiplier, control)
        await this.updateAmount(amount, control)
        if(this._betButton_1 == null || this._betButton_2 == null){
            sendLogToGUI({
                location: "BetControl",
                message: "bet :: bet button null. control"
            }, LogCode.EXCEPTION)
            throw "bet: bet button null. control"
        }
        if(control === Control.Control1){
            await this._betButton_1.click({delay: this._randomDelay()})
            //await this.aviatorPage.waitForTimeout(1000)
            return
        }
        await this._betButton_2.click({delay: this._randomDelay()})
        //await this.aviatorPage.waitForTimeout(1000)
    }
}