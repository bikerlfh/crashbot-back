// export const URL_AVIATOR_DEMO: string = "https://www.spribe.co/games/aviator"
// export const URL_BETPLAY: string = "https://betplay.com.co/slots"

import { Dictionary } from "./types/interfaces"
import { AviatorBetPlay } from "./aviator/AviatorBetPlay"
import { AviatorDemo } from "./aviator/AviatorDemo"
import { AviatorOneWin } from "./aviator/AviatorOneWin"


export const WEB_SOCKET_URL: string = process.env.WEB_SOCKET_URL || "ws://localhost:8000/bot/"

export class HomeBet{
    id: number
    minBet: number
    maxBet: number
    url: string
    amountMultiple: number|null = null
    aviatorPage: any
    username: string|null
    password: string|null

    constructor(obj: any){
        this.id = obj.id
        this.minBet = obj.minBet
        this.maxBet = obj.maxBet
        this.url = obj.url
        this.aviatorPage = obj.aviatorPage
        this.username = obj.hasOwnProperty('username')? obj.username: null
        this.password = obj.hasOwnProperty('password')? obj.password: null
    }

    getAviatorPage(){
        return new this.aviatorPage(this.url)
    }

}

export const HomeBets: Dictionary<HomeBet> = {
    demo: new HomeBet({
        id: 1,
        minBet: 0.1,
        maxBet: 100,
        url: "https://www.spribe.co/games/aviator",
        aviatorPage: AviatorDemo
    }),
    betplay: new HomeBet({
        id: 2,
        minBet: 100,
        maxBet: 50000,
        url: "https://betplay.com.co/slots",
        amountMultiple: 100,
        aviatorPage: AviatorBetPlay
    }),
    oneWin: new HomeBet({
        id: 3,
        minBet: 500,
        maxBet: 500000, 
        url: "https://1wslue.top/casino/",
        amountMultiple: 100,
        aviatorPage: AviatorOneWin
    }),
    rivalo: new HomeBet({
        id: 4,
        minBet: 500,
        maxBet: 500000, 
        url: "https://www.rivalo.co",
        amountMultiple: 100,
        aviatorPage: AviatorDemo
    }),
}
