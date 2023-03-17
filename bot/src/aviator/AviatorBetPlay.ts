import playwright from 'playwright'
import {AviatorPage} from './Aviator'
import { HomeBets } from '../constants'

export class AviatorBetPlay extends AviatorPage{
    _frame: playwright.FrameLocator| null = null

    async _login(): Promise<void> {
        if(!this._page){
            throw "_login :: page is null"
        }
        const userNameInput = this._page.locator("input#userName")
        const passwordInput = this._page.locator("input#password")
        const loginButton = this._page.locator("button#btnLoginPrimary")
        await userNameInput.type(HomeBets.betplay.username || "", {delay: 100})
        await passwordInput.type(HomeBets.betplay.password || "", {delay: 100})
        this._click(loginButton)
        await this._page.locator("#spanUser").waitFor({timeout: 50000})
        const searchButton = this._page.locator("input.inputSearch")
        await searchButton.type("aviator", {delay: 150})
        await this._page.waitForTimeout(2000)
        this._click(this._page.locator("button.btnSlot"))
        // this._page.goto(HomeBet.betplay.aviatorUrl)
    }

    async _getAppGame(): Promise<playwright.Locator> {
        if(!this._page){
            throw "_getAppGame :: page is null"
        }
        await this._page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", {timeout: 50000})
        while(true){
            try {
                // gameFrame
                // spribe-game
                this._frame = this._page.frameLocator("#gameFrame").frameLocator("#spribe-game")
                this._appGame = this._frame.locator("app-game").first()
                await this._appGame.locator(".result-history").waitFor({
                    timeout: 5000
                });
                return this._appGame
            } catch (e) {
                if (e instanceof playwright.errors.TimeoutError) {
                    console.log("error timeout")
                    continue
                }
                throw e
            }
        }
    }
    
    async readGameLimits(){
        if(this._frame == null){
            throw "readGameLimits :: _frame is null"
        }
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
        const limits = await this._frame.locator("app-game-limits ul>li>span").all()
        this.minimumBet = parseFloat((await limits[0].textContent())?.split(" ")[0] || "0")
        this.maximumBet = parseFloat((await limits[1].textContent())?.split(" ")[0] || "0")
        this.maximumWinForOneBet =  parseFloat((await limits[2].textContent())?.split(" ")[0] || "0")
        console.log("minimumBet: ", this.minimumBet)
        console.log("maximumBet: ", this.maximumBet)
        console.log("maximumWinForOneBet: ", this.maximumWinForOneBet)
        const buttonClose = this._frame.locator("ngb-modal-window")
        await buttonClose.click()
    }
}