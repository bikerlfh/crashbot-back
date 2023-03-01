import playwright from 'playwright'
import {AviatorPage} from './Aviator'
import { HomeBet } from '../constants'

export class AviatorDemo extends AviatorPage{
    _frame: playwright.FrameLocator| null = null

    constructor(){
        super(HomeBet.demo.url)
    }
    async _login(): Promise<void> {
        if(!this._page || !this._context){
            throw "_login :: page or context are null"
        }
        await this._page.getByRole('button', { name: 'Play Demo' }).click();
        await this._page.getByRole('button', { name: "Yes I’m over 18" }).click();
        await this._page.waitForTimeout(2000);
        let pages = this._context.pages();
        this._page =pages[1]
    }
}