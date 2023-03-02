import { APIRest } from "./ApiRest";


export let AviatorBotAPI = {
    save_multipliers(homeBetId: number, multipliers: number[]){
        const url = "/homebet/multiplier/add/"
        return APIRest.post(url, {
            home_bet_id: homeBetId,
            multipliers: multipliers
        })
    }
}