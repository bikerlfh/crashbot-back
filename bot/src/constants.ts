// export const URL_AVIATOR_DEMO: string = "https://www.spribe.co/games/aviator"
// export const URL_AVIATOR_DEMO: string = "https://aviator-demo.spribegaming.com/?currency=USD&operator=demo&jurisdiction=CW&lang=EN&return_url=https:%2F%2Fspribe.co%2Fgames&user=59702&token=s7p0PCPnR5mp2yyQilRG0QdUrV0CiS2l"
// export const URL_BETPLAY: string = "https://betplay.com.co/slots"

import { Dictionary } from "./types/interfaces"
import { AviatorBetPlay } from "./aviator/AviatorBetPlay"
import { AviatorDemo } from "./aviator/AviatorDemo"
import { AviatorOneWin } from "./aviator/AviatorOneWin"

export class HomeBet{
    id: number
    minBet: number
    maxBet: number
    aviatorPage: AviatorDemo|AviatorBetPlay|AviatorOneWin
    username: string|null
    password: string|null

    constructor(obj: Dictionary<any>){
        this.id = obj.id
        this.minBet = obj.minBet
        this.maxBet = obj.maxBet
        this.aviatorPage = obj.aviatorPage
        this.username = obj.hasOwnProperty('username')? obj.username: null
        this.password = obj.hasOwnProperty('password')? obj.password: null
    }
}

export const HomeBets: Dictionary<HomeBet> = {
    demo: new HomeBet({
        id: 1,
        minBet: 0.1,
        maxBet: 100,
        aviatorPage: new AviatorDemo("https://www.spribe.co/games/aviator")
    }),
    betplay: new HomeBet({
        id: 2,
        minBet: 5000,
        maxBet: 50000, 
        username: process.env.BET_PLAY_USERNAME,
        password: process.env.BET_PLAY_PASSWORD,
        aviatorPage: new AviatorBetPlay("https://betplay.com.co/slots")
    }),
    oneWin: new HomeBet({
        id: 3,
        minBet: 500,
        maxBet: 500000, 
        username: process.env.ONE_WIN_USERNAME,
        password: process.env.ONE_WIN_PASSWORD,
        aviatorPage: new AviatorOneWin("https://1wslue.top/casino/")
    }),
    rivalo: new HomeBet({
        id: 4,
        minBet: 500,
        maxBet: 500000, 
        aviatorPage: new AviatorDemo("https://www.rivalo.co")
    }),
}
