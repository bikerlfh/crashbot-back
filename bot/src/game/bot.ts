import { generateRandomMultiplier, roundNumber, kellyFormula, adaptiveKellyFormula } from "./utils"
import { BotStrategy } from "../api/models"
import { PredictionCore } from "./PredictionCore"
import { Bet } from "./core"
import { AviatorBotAPI } from "../api/AviatorBotAPI"


export enum BotType{
    AGGRESSIVE = "aggressive",
    TIGHT = "tight",
    LOOSE = "loose",
}


export class Bot{
    /*
    * The Player class is a class used to determine the optimal fraction of one's capital to bet on a given bet.
    * @param {number} STOP_LOSS_PERCENTAGE: use to calculate stop loss
    * @param {number} TAKE_PROFIT_PERCENTAGE: use to calculate take profit
    * @param PROFIT_STRATEGIES is the amount of money you have to bet  
    */

    BOT_TYPE: BotType = BotType.LOOSE
    RISK_FACTOR: number = 0.1 // 0.1 = 10%
    MIN_MULTIPLIER_TO_BET: number = 1.5
    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 0.8 // 0.8 = 80%
    MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET: number = 0.8 // 0.8 = 80%
    MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET: number = 0.8 // 0.8 = 80%
    STOP_LOSS_PERCENTAGE: number = 0
    TAKE_PROFIT_PERCENTAGE: number = 0

    private STRATEGIES: BotStrategy[] = []
    
    private initialBalance: number = 0
    private balance: number = 0
    private stopLoss: number = 0
    private takeProfit: number = 0
    private minimumBet: number
    private maximumBet: number
    private bets: Bet[] = []
    // betting amount lossess in order
    private betAmountLosses: number[] = []

    constructor(
        botType: BotType,
        minimumBet: number = 0,
        maximumBet: number = 0
    ){
        this.BOT_TYPE = botType
        this.minimumBet = minimumBet
        this.maximumBet = maximumBet
    }

    async initialize(balance: number){
        this.initialBalance = balance
        this.balance = balance
        const bot_data = await AviatorBotAPI.requestGetBots(this.BOT_TYPE)
        if(bot_data.length == 0){
            throw new Error("No bot data found")
        }
        const bot = bot_data[0]
        this.MIN_CATEGORY_PERCENTAGE_TO_BET = bot.minCategoryPercentageToBet
        this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET = bot.minCategoryPercentageValueInLiveToBet
        this.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET = bot.minAveragePredictionModelInLiveToBet
        this.RISK_FACTOR = bot.riskFactor
        this.MIN_MULTIPLIER_TO_BET = bot.minMultiplierToBet
        this.STOP_LOSS_PERCENTAGE = bot.stopLossPercentage
        this.TAKE_PROFIT_PERCENTAGE = bot.takeProfitPercentage
        this.STRATEGIES = bot.strategies
        this.stopLoss = this.initialBalance * (this.STOP_LOSS_PERCENTAGE)
        this.takeProfit = this.initialBalance * (this.TAKE_PROFIT_PERCENTAGE)
        console.log("Bot initialized")
        console.log("Bot type: ", this.BOT_TYPE)
        console.log("Bot risk factor: ", this.RISK_FACTOR)
        console.log("Bot min multiplier to bet: ", this.MIN_MULTIPLIER_TO_BET)
        console.log("Bot min category percentage to bet: ", this.MIN_CATEGORY_PERCENTAGE_TO_BET)
        console.log("Bot min category percentage value in live to bet: ", this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET)
        console.log("Bot min average prediction model in live to bet: ", this.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET)
        console.log("stopLoss: ", this.stopLoss)
        console.log("takeProfit: ", this.takeProfit)
        console.log("Bot strategies count: ", this.STRATEGIES.length)
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

    private getStrategy(numberOfBets: number): BotStrategy|undefined{
        let profit = this.getProfitPercent()
        let strategies = this.STRATEGIES.filter((s)=>
            numberOfBets >= s.numberOfBets && profit >= s.profitPercentage
        )
        return strategies.length > 0? strategies.slice(-1)[0]: undefined
    }

    private addLoss(amount: number){
        this.betAmountLosses.push(amount)
    }

    private removeLoss(amount: number){
        let totalLoss = amount
        for(let i = this.betAmountLosses.length - 1; i >= 0; i--){
            if(this.betAmountLosses[i] > totalLoss){
                this.betAmountLosses[i] -= totalLoss
                break
            }
            totalLoss -= this.betAmountLosses[i]
            this.betAmountLosses.pop()
        }
    }

    evaluateBets(multiplierResult: number){
        let totalAmount = 0
        this.bets.forEach((bet)=>{
            const profit = bet.evaluate(multiplierResult)
            if (profit < 0){
                this.addLoss(bet.amount)
            }
            else{
                totalAmount += profit
            }
        })
        if(totalAmount > 0){
            this.removeLoss(totalAmount)
        }
        this.bets = []
    }
    
    getNumberOfBets(): number{
        /*
        * number of maximum bets that the bot can hold
        * @return {number} the number of bets
        */
        return roundNumber(this.balance / this.maximumBet, 0)
    }

    getProfit(): number{
        return roundNumber(this.balance - this.initialBalance, 2)
    }

    getProfitPercent(): number{
        return this.getProfit() / this.initialBalance
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

    private calculateAmountToRecoverLosses(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        const profit = this.getProfit()
        if(profit >= 0 || multiplier < this.MIN_MULTIPLIER_TO_BET){
            return []
        }
        let amount = (Math.abs(profit) / (multiplier - 1))
        console.log("******** BAD PROFIT ********")
        console.log("amountToRecover", amount)
        console.log("betAmountLosses", this.betAmountLosses)
        this.bets = []
        if(amount >= this.maximumBet){
            amount = (this.betAmountLosses.slice(-1)[0] / (multiplier - 1))
        }
        const minBet = this.balance * strategy.minAmountPercentageToBet
        console.log("minBet", minBet)
        if(amount > minBet){
            amount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
            console.log("adaptiveKellyFormula", amount)
        }
        if(amount > this.maximumBet){
            amount = this.maximumBet * 0.5
        }
        if(amount > this.balance){
            amount = this.balance
        }
        if(amount < this.maximumBet && amount < this.balance){
            if(multiplier >= 2){
                const amount1 = roundNumber(amount / 2, 0)
                const multiplier1 = roundNumber((multiplier / 2) * 1.5, 2)
                this.bets.push(new Bet(amount1, multiplier1))
                this.bets.push(new Bet(amount1, multiplier1))
            }else{
                this.bets.push(new Bet(amount, multiplier))
            }
        }
        this.bets = this.bets.filter((b)=> b.amount > 0)
        return this.bets
    }

    calculateAmountBet(
        multiplier: number, 
        probability: number,
        strategy: BotStrategy, 
        usedAmount?: number
    ): number{
        usedAmount = usedAmount || 0
        let profit = this.getProfit()
        const balance = this.initialBalance - usedAmount
        const minBet = balance * (strategy.minAmountPercentageToBet)
        let amount = 0
        if(usedAmount == 0){
            amount = minBet + profit * (strategy.profitPercentageToBet)
        }else{
            amount = usedAmount / 3
        }
        console.log("******** GOOD PROFIT ********")
        console.log("minBet: ", minBet, "; amount: ", amount)
        amount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
        console.log("kelly amount", amount)
        if(amount > 0){
            amount = this.validateBetAmount(amount)
        }
        console.log("validateBetAmount", amount)
        console.log("*****************************")
        return amount
    }

    private generateBets(
        prediction: PredictionCore,
        strategy: BotStrategy,
    ): Bet[]{
        this.bets = []
        const profit = this.getProfit()
        const categoryPrecentage = prediction.getCategoryPercentage()
        const predictionRound = prediction.getPredictionRoundValue()
        let predictionValue = prediction.getPreditionValue()
        const categoryPercentageValueInLive = prediction.geCategoryPercentageValueInLive()
        const inCategoryPercentageValueInLive = categoryPercentageValueInLive >= this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET
        let amount: number = 0
        let multiplier: number = 0
        if(profit < 0){
            let multiplier = predictionRound == 1? predictionValue: 2
            this.bets = this.calculateAmountToRecoverLosses(multiplier, categoryPrecentage, strategy)
            return this.bets
        }
        // profit >= 0
        switch(predictionRound){
            case 1:
                amount = this.calculateAmountBet(predictionValue, categoryPrecentage, strategy)
                this.bets.push(new Bet(amount, predictionValue))
                break
            case 2:
                multiplier = inCategoryPercentageValueInLive? predictionValue: 1.95
                amount = this.calculateAmountBet(multiplier, categoryPrecentage, strategy)
                this.bets.push(new Bet(amount, multiplier))
                multiplier = generateRandomMultiplier(2, 3)
                amount = this.calculateAmountBet(multiplier, categoryPrecentage, strategy, amount)
                this.bets.push(new Bet(amount, multiplier))
                break
            case 3:
                multiplier = inCategoryPercentageValueInLive? predictionValue: generateRandomMultiplier(2, 3.5)
                amount = this.calculateAmountBet(multiplier, categoryPrecentage, strategy)
                this.bets.push(new Bet(amount, multiplier))
                break
        }
        this.bets = this.bets.filter((b)=> b.amount > 0)
        return this.bets
    }

    getNextBet(prediction: PredictionCore): Bet[]{
        if(prediction == null){
            return []
        }
        const numberOfBet = this.getNumberOfBets()
        const strategy = this.getStrategy(numberOfBet)
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
        const categoryPercentageValueInLive = prediction.geCategoryPercentageValueInLive()
        const averagePredictionsOfModel = prediction.averagePredictionsOfModel
        console.log("\nprofit: ", profit)
        console.log("predictionRound: ", predictionRound)
        console.log("predictionValue: ", predictionValue)
        console.log("categoryPrecentage: ", categoryPrecentage)
        console.log("categoryPercentageValueInLive: ", categoryPercentageValueInLive)
        console.log("averagePredictionsOfModel: ", averagePredictionsOfModel)
        const inCategoryPercentageValueInLive = categoryPercentageValueInLive >= this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET
        console.log("inCategoryPercentageValueInLive: ", inCategoryPercentageValueInLive)
        const inCategoryPrecentage = categoryPrecentage >= this.MIN_CATEGORY_PERCENTAGE_TO_BET
        console.log("inCategoryPrecentage: ", inCategoryPrecentage)
        const inAveragePredictionsOfModel = averagePredictionsOfModel >= this.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET
        console.log("inAveragePredictionsOfModel: ", inAveragePredictionsOfModel)
        if(this.inStopLoss()){
            console.log("player :: Stop loss reached")
            return []
        }
        if(this.inTakeProfit()){
            console.log("player :: Take profit reached")
            return []
        }
        if(!inCategoryPrecentage){
            return []
        }
        if(predictionValue < this.MIN_MULTIPLIER_TO_BET){
            console.log("Bot :: Prediction value is too low")
            return []
        }
        // CATEGORY 1
        if(predictionRound == 1){
            if(!inCategoryPercentageValueInLive || predictionValue < 1.2){
                return []
            }
            return this.generateBets(prediction, strategy)
        }
        if(!inAveragePredictionsOfModel){
            return []
        }
        // CATEGORY 2 and 3
        return this.generateBets(prediction, strategy)
    }
}