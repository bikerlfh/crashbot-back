import { generateRandomMultiplier, roundNumber } from "./utils"
import { PlayerStrategy } from "../api/models"
import { PredictionCore } from "./PredictionCore"
import { Bet } from "./core"
import { AviatorBotAPI } from "../api/AviatorBotAPI"


export enum PlayerType{
    AGGRESSIVE = "aggressive",
    TIGHT = "tight",
    LOOSE = "loose",
}


export class Player{
    /*
    * The Player class is a class used to determine the optimal fraction of one's capital to bet on a given bet.
    * @param {number} STOP_LOSS_PERCENTAGE: use to calculate stop loss
    * @param {number} TAKE_PROFIT_PERCENTAGE: use to calculate take profit
    * @param PROFIT_STRATEGIES is the amount of money you have to bet  
    */

    PLAYER_TYPE: PlayerType = PlayerType.LOOSE

    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 80
    MIN_AVERAGE_PREDICTION_IN_LIVE_TO_BET: number = 80
    MIN_AVERAGE_PREDICTION_VALUES_IN_LIVE_TO_BET: number = 80

    STOP_LOSS_PERCENTAGE: number = 0
    TAKE_PROFIT_PERCENTAGE: number = 0

    private PLAYER_STRATEGIES: PlayerStrategy[] = []
    
    private initialBalance: number = 0
    private balance: number = 0
    private stopLoss: number = 0
    private takeProfit: number = 0
    private minimumBet: number
    private maximumBet: number

    constructor(
        minimumBet: number = 0,
        maximumBet: number = 0
    ){
        this.minimumBet = minimumBet
        this.maximumBet = maximumBet
    }

    static getInstance(
        minimumBet: number = 0,
        maximumBet: number = 0,
        playerType: PlayerType,
    ): Player{
        switch(playerType){
            case PlayerType.AGGRESSIVE:
                return new AggressivePlayer(minimumBet, maximumBet)
            case PlayerType.TIGHT:
                return new TightPlayer(minimumBet, maximumBet)
            case PlayerType.LOOSE:
                return new LoosePlayer(minimumBet, maximumBet)
            default:
                throw new Error("Invalid player type")
        }
    }

    async initialize(balance: number){
        this.initialBalance = balance
        this.balance = balance
        this.stopLoss = this.initialBalance * (this.STOP_LOSS_PERCENTAGE / 100)
        this.takeProfit = this.initialBalance * (this.TAKE_PROFIT_PERCENTAGE / 100)
        this.PLAYER_STRATEGIES = (
            await AviatorBotAPI.requestGetStrategies()
        ).filter((s)=> s.strategyType == this.PLAYER_TYPE)
        console.log("stopLoss: ", this.stopLoss)
        console.log("takeProfit: ", this.takeProfit)
        console.log("Player strategies: ", this.PLAYER_STRATEGIES)
    }

    private validateBetAmount(amount: number): number{
        if(amount < this.minimumBet){
            amount = this.minimumBet
        }
        else if(amount > this.maximumBet){
            amount = this.maximumBet
        }
        if(amount > this.balance){
            amount = this.balance
        }
        return roundNumber(amount, 0)
    }

    private getStrategy(): PlayerStrategy|undefined{
        let profit = this.getProfitPercent()
        const numOfBets = this.getNumberOfBets()
        let strategies = this.PLAYER_STRATEGIES.filter((s)=>
            numOfBets >= s.numberOfBets && profit >= s.profitPercentage
        )
        return strategies.length > 0? strategies.slice(-1)[0]: undefined
    }
    
    getNumberOfBets(): number{
        return roundNumber(this.balance / this.minimumBet, 0)
    }

    getProfit(): number{
        return this.balance - this.initialBalance
    }

    getProfitPercent(): number{
        return this.getProfit() / this.initialBalance * 100
    }

    inStopLoss(): boolean{
        const profit = this.getProfit()
        return profit < 0 && Math.abs(profit) >= this.stopLoss
    }
    
    inTakeProfit(): boolean{
        const profit = this.getProfit()
        return profit >= this.takeProfit
    }

    updateBalance(balance: number){
        this.balance = balance
    }

    calculateAmountBet(multiplier: number, strategy: PlayerStrategy, usedAmount?: number): number{
        usedAmount = usedAmount || 0
        let profit = this.getProfit()
        const balance = this.balance - usedAmount
        const minBet = balance * (strategy.minBalancePercentageToBetAmount / 100)
        let amount = 0
        if(profit < 0){
            amount = (Math.abs(profit) / (multiplier - 1)) + minBet
        }
        else if(usedAmount <= 0){
            amount = minBet + profit * (strategy.profitPercentageToBetAmount / 100)
        }
        else{
            amount = usedAmount / 3
        }
        amount = this.validateBetAmount(amount)
        return amount
    }

    getNextBet(prediction: PredictionCore): Bet[]{
        if(this.inStopLoss()){
            console.log("player :: Stop loss reached")
            return []
        }
        if(this.inTakeProfit()){
            console.log("player :: Take profit reached")
            return []
        }
        if(prediction == null){
            return []
        }
        const strategy = this.getStrategy()
        if(!strategy){
            console.warn(
                "No strategy found for profit percentage: ", this.getProfitPercent()
            )
            return []
        }
        const profit = this.getProfit()
        const categoryPrecentage = prediction.getCategoryPercentage()
        const predictionRound = prediction.getPredictionRoundValue()
        let predictionValue = prediction.getPreditionValue()
        const averagePredictionValuesInLive = prediction.averagePredictionValuesInLive
        const averagePredictionInLive = prediction.averagePredictionInLive
        console.log("player :: profit: ", profit)
        console.log("player :: categoryPrecentage: ", categoryPrecentage)
        console.log("player :: predictionRound: ", predictionRound)
        console.log("player :: predictionValue: ", predictionValue)
        console.log("player :: averagePredictionValuesInLive: ", averagePredictionValuesInLive)
        console.log("player :: averagePredictionInLive: ", averagePredictionInLive)
        const inAveragePredictionValuesInLive = averagePredictionValuesInLive >= this.MIN_AVERAGE_PREDICTION_VALUES_IN_LIVE_TO_BET
        const inCategoryPrecentage = categoryPrecentage >= this.MIN_CATEGORY_PERCENTAGE_TO_BET
        const inAveragePredictionInLive = averagePredictionInLive >= this.MIN_AVERAGE_PREDICTION_IN_LIVE_TO_BET
        if(!inCategoryPrecentage){
            return []
        }
        const bets: Bet[] = []
        // CATEGORY 1
        if(predictionRound == 1){
            if(!inAveragePredictionValuesInLive || predictionValue < 1){
                return []
            }
            const amount = this.calculateAmountBet(predictionValue, strategy)
            return [new Bet(amount, predictionValue)]
        }
        if(!inAveragePredictionInLive){
            return []
        }
        // CATEGORY 2
        if(predictionRound == 2){
            if(profit < 0){
                bets.push(new Bet(this.calculateAmountBet(1.95, strategy), 1.95))
            }else{
                const amount = this.calculateAmountBet(1.95, strategy)
                const multiplier = generateRandomMultiplier(2, 2.8)
                bets.push(new Bet(amount, 1.95))
                bets.push(new Bet(this.calculateAmountBet(multiplier, strategy), multiplier))
            }
            return bets
        }    
        // CATEGORY 3
        if(profit > 0){
            bets.push(new Bet(this.calculateAmountBet(predictionRound, strategy), predictionRound))
            return bets
        }
        const amount = this.calculateAmountBet(1.95, strategy)
        bets.push(new Bet(amount, 1.95))
        return bets
    }
}

export class AggressivePlayer extends Player{
    PLAYER_TYPE: PlayerType = PlayerType.AGGRESSIVE
    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 55
    MIN_AVERAGE_PREDICTION_IN_LIVE_TO_BET: number = 55
    MIN_AVERAGE_PREDICTION_VALUES_IN_LIVE_TO_BET: number = 70
    STOP_LOSS_PERCENTAGE: number = 20
    TAKE_PROFIT_PERCENTAGE: number = 200
}

export class TightPlayer extends Player{
    PLAYER_TYPE: PlayerType = PlayerType.TIGHT
    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 69
    MIN_AVERAGE_PREDICTION_IN_LIVE_TO_BET: number = 69
    MIN_AVERAGE_PREDICTION_VALUES_IN_LIVE_TO_BET: number = 69
    STOP_LOSS_PERCENTAGE: number = 20
    TAKE_PROFIT_PERCENTAGE: number = 50
}

export class LoosePlayer extends Player{
    PLAYER_TYPE: PlayerType = PlayerType.LOOSE
    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 90
    MIN_AVERAGE_PREDICTION_IN_LIVE_TO_BET: number = 90
    MIN_AVERAGE_PREDICTION_VALUES_IN_LIVE_TO_BET: number = 90
    STOP_LOSS_PERCENTAGE: number = 20
    TAKE_PROFIT_PERCENTAGE: number = 50
}
