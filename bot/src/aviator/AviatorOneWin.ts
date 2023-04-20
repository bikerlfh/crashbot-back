import playwright from 'playwright'
import {AviatorPage} from './Aviator'
import { HomeBets } from '../constants'
import {sendEventToGUI} from "../ws/gui_events"


export class AviatorOneWin extends AviatorPage{
    _frame: playwright.FrameLocator| null = null


    async _login(): Promise<void> {
        if(!this._page){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "_login :: page is null"
            })
            throw "_login :: page is null"
        }
        const pageLoginButton = this._page.locator("button.login")
        await this._click(pageLoginButton)
        await this._page.waitForTimeout(1000)
        const userNameInput = this._page.locator("input[name='login']")
        const passwordInput = this._page.locator("input[name='password']")
        await userNameInput.type(HomeBets.oneWin.username || "", {delay: 100})
        await passwordInput.type(HomeBets.oneWin.password || "", {delay: 100})
        await this._page.waitForTimeout(1000)
        const loginButton_2 = this._page.locator("button.modal-button[type='submit']")
        await this._click(loginButton_2)
        await this._page.waitForTimeout(2000)
    }

    async _getAppGame(): Promise<playwright.Locator> {
        if(!this._page){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "_getAppGame :: page is null"
            })
            throw "_getAppGame :: page is null"
        }
        await this._page.waitForURL("**/casino/play/spribe_aviator**", {timeout: 50000})
        while(true){
            try {
                this._frame = this._page.locator(".CasinoGamePromoted_game_vXIG_").frameLocator("[src^=https]")
                this._appGame = this._frame.locator("app-game").first()
                await this._appGame.locator(".result-history").waitFor({
                    timeout: 5000
                });
                return this._appGame
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    sendEventToGUI.log.debug("page :: error timeout")
                    continue
                }
                throw e
            }
        }
    }
    
    async readGameLimits(){
        if(this._frame == null){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "readGameLimits :: _frame is null"
            })
            throw "readGameLimits :: _frame is null"
        }
        if(this._appGame == null || this._page == null){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "readGameLimits :: _appGame is null"
            })
            throw "readGameLimits :: _appGame is null"
        }
        const menu = this._appGame.locator(".dropdown-toggle.user")
        if(menu == null){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "readGameLimits :: menu is null"
            })
            throw "readGameLimits :: menu is null"
        }
        // await menu.click()
        this._click(menu)
        await this._page.waitForTimeout(400);
        // app-settings-menu
        // app-user-menu-dropdown
        const appUserMenu = this._appGame.locator("app-settings-menu")
        if(appUserMenu == null){
            sendEventToGUI.exception({
                location: "AviatorOneWin",
                message: "readGameLimits :: appusermenu is null"
            })
            throw "readGameLimits :: appusermenu is null"
        }
        const listMenu = appUserMenu.locator(".list-menu").last()
        const menuLimits = listMenu.locator(".list-menu-item").last()
        await menuLimits.click()
        await this._page.waitForTimeout(400);
        const limits = await this._frame.locator("app-game-limits ul>li>span").all()
        this.minimumBet = parseFloat((await limits[0].textContent())?.split(" ")[0] || "0")
        this.maximumBet = parseFloat((await limits[1].textContent())?.split(" ")[0] || "0")
        this.maximumWinForOneBet =  parseFloat((await limits[2].textContent())?.split(" ")[0] || "0")
        sendEventToGUI.log.debug(`minimumBet: ${this.minimumBet}`)
        sendEventToGUI.log.debug(`maximumBet: ${this.maximumBet}`)
        sendEventToGUI.log.debug(`maximumWinForOneBet: ${this.maximumWinForOneBet}`)
        const buttonClose = this._frame.locator("ngb-modal-window")
        await buttonClose.click()
    }
}