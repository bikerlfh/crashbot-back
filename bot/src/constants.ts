// export const URL_AVIATOR_DEMO: string = "https://www.spribe.co/games/aviator"
// export const URL_AVIATOR_DEMO: string = "https://aviator-demo.spribegaming.com/?currency=USD&operator=demo&jurisdiction=CW&lang=EN&return_url=https:%2F%2Fspribe.co%2Fgames&user=59702&token=s7p0PCPnR5mp2yyQilRG0QdUrV0CiS2l"
// export const URL_BETPLAY: string = "https://betplay.com.co/slots"

import { Dictionary } from "./types/interfaces"

export class HomeBet{
    id: number
    url: string
    minBet: number
    maxBet: number
    username: string|null
    password: string|null

    constructor(obj: Dictionary<any>){
        this.id = obj.id
        this.url = obj.url
        this.minBet = obj.minBet
        this.maxBet = obj.maxBet
        this.username = obj.hasOwnProperty('username')? obj.username: null
        this.password = obj.hasOwnProperty('password')? obj.password: null
    }
}

export let HomeBets: Dictionary<HomeBet>= {
    demo: new HomeBet({
        id: 1,
        url: "https://www.spribe.co/games/aviator",
        minBet: 0.1,
        maxBet: 100
    }),
    betplay: new HomeBet({
        id: 2,
        url: "https://betplay.com.co/slots",
        minBet: 100,
        maxBet: 50000, 
        username: process.env.BET_PLAY_USERNAME,
        password: process.env.BET_PLAY_PASSWORD
    }),
    oneWin: new HomeBet({
        id: 3,
        url: "https://1wslue.top/casino/", 
        minBet: 500,
        maxBet: 500000, 
        username: process.env.ONE_WIN_USERNAME,
        password: process.env.ONE_WIN_PASSWORD
    }),
    rivalo: new HomeBet({
        id: 4,
        url: "https://www.rivalo.co",
        minBet: 500,
        maxBet: 500000, 
    }),
}
