import { makeWSError } from "./utils"
import {login, verifyToken} from "./handlers"
import {BotType} from "../game/core"
import { HomeBets } from "../constants"
import {Game} from "../game/GameAdvance"


export const verifyTokenEvent = async (): Promise<any> => {
    return await verifyToken(null)
}

export const loginEvent = async (data: any): Promise<any|boolean> => {
    const username = data.username
    const password = data.password
    if(!username || !password){
        return makeWSError('username and password are required')
    }
    return await login(username, password)
}


export const autoPlayEvent = (data: any): any => {
    const autoPlay = data.autoPlay
    if(autoPlay === undefined){
        return makeWSError('autoPlay is required')
    }
    (global as any).autoPlay = autoPlay
    return {autoPlay: (global as any).autoPlay}
}

export const setMaxAmountToBetEvent = (data: any): any => {
    const maxAmountToBet = data.maxAmountToBet;
    if(maxAmountToBet === undefined){
        return makeWSError('maxAmountToBet is required')
    }
    const game:Game = (global as any).game;
    if(!game){
        return makeWSError('the game is not running')
    }
    (global as any).maxAmountToBet = maxAmountToBet;
    game.bot.setMaxAmountToBet(maxAmountToBet);
    return {maxAmountToBet: (global as any).maxAmountToBet}
}

export const closeGameEvent = async (data: any): Promise<any> => {
    const game: Game = (global as any).game
    await game.close();
    (global as any).game = null;
    return {closed: true}
}


export const startBotEvent =  async (data: any): Promise<any> => {
    const botType = data.botType
    const homeBetId = data.homeBetId
    const maxAmountToBet = data.maxAmountToBet
    if(!botType || !homeBetId || !maxAmountToBet){
        throw makeWSError('botType, homeBetId and maxAmountToBet are required')
    }
    const homeBetKey = Object.keys(HomeBets).find(key => HomeBets[key].id === homeBetId)
	if(!homeBetKey){
        throw makeWSError("invalid homeBetId")
    }
    let botTypeSelected = BotType.AGGRESSIVE
    switch(botType){
		case "aggressive":
			botTypeSelected = BotType.AGGRESSIVE
			break;
		case "tight":
			botTypeSelected = BotType.TIGHT
            break;
        case "loose":
            botTypeSelected = BotType.LOOSE
			break;
        default:
            throw makeWSError("invalid botType")
	}
    (global as any).maxAmountToBet = maxAmountToBet;
    const homeBet = HomeBets[homeBetKey];
    let game: Game = (global as any).game
    if(game){
        throw makeWSError('the game is already running')
    }
    (global as any).game = new Game(homeBet, botTypeSelected, true);
    game = (global as any).game
	try{
		await game.initialize()
		await game.play()
	}catch(e){
		console.log(e)
	}
}
