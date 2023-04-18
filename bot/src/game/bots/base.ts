import { generateRandomMultiplier, roundNumber, adaptiveKellyFormula, formatNumberToMultiple } from "../utils"
import { BotStrategy } from "../../api/models"
import { PredictionCore } from "../PredictionCore"
import { Bet, PredictionData } from "../core"
import { AviatorBotAPI } from "../../api/AviatorBotAPI"
import {BotType} from "../core"


export class BotBase{
    /*
    * The BotBase has the logict to all bots
    * @param {number} STOP_LOSS_PERCENTAGE: use to calculate stop loss
    * @param {number} TAKE_PROFIT_PERCENTAGE: use to calculate take profit
    * @param PROFIT_STRATEGIES is the amount of money you have to bet  
    */

    BOT_TYPE: BotType = BotType.LOOSE
    RISK_FACTOR: number = 0.1 // 0.1 = 10%
    MIN_MULTIPLIER_TO_BET: number = 1.5
    MIN_MULTIPLIER_TO_RECOVER_LOSSES: number = 2.0
    MIN_CATEGORY_PERCENTAGE_TO_BET: number = 0.8 // 0.8 = 80%
    MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET: number = 0.8 // 0.8 = 80%
    MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET: number = 0.8 // 0.8 = 80%
    STOP_LOSS_PERCENTAGE: number = 0
    TAKE_PROFIT_PERCENTAGE: number = 0

    protected STRATEGIES: BotStrategy[] = []
    protected amountMultiple: number|null = null
    protected initialBalance: number = 0
    protected balance: number = 0
    protected stopLoss: number = 0
    protected takeProfit: number = 0
    protected minimumBet: number
    protected maximumBet: number
    protected bets: Bet[] = []
    // betting amount lossess in order
    protected amountsLost: number[] = []

    /*
    * only use for bots that want to bet a fixed amount
    * the min amount of bet should be less than the max amount of bet / 3 example: max bet = 300, min bet = 300/3 = 100
    */
    protected _maxAmountToBet: number = 0
    protected _minAmountToBet: number = 0

    constructor(
        botType: BotType,
        minimumBet: number = 0,
        maximumBet: number = 0,
        amountMultiple?: number
    ){
        this.BOT_TYPE = botType
        this.minimumBet = minimumBet
        this.maximumBet = maximumBet
        this.amountMultiple = amountMultiple || null
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
        this.MIN_MULTIPLIER_TO_RECOVER_LOSSES = bot.minMultiplierToRecoverLosses
        
        this.STOP_LOSS_PERCENTAGE = bot.stopLossPercentage
        this.TAKE_PROFIT_PERCENTAGE = bot.takeProfitPercentage
        this.STRATEGIES = bot.strategies
        this.stopLoss = this.initialBalance * (this.STOP_LOSS_PERCENTAGE)
        this.takeProfit = this.initialBalance * (this.TAKE_PROFIT_PERCENTAGE)
        console.log("Bot initialized")
        console.log("Bot type: ", this.BOT_TYPE)
        console.log("Bot risk factor: ", this.RISK_FACTOR)
        console.log("Bot min multiplier to bet: ", this.MIN_MULTIPLIER_TO_BET)
        console.log("Bot min multiplier to recover losses: ", this.MIN_MULTIPLIER_TO_RECOVER_LOSSES)
        console.log("Bot min category percentage to bet: ", this.MIN_CATEGORY_PERCENTAGE_TO_BET)
        console.log("Bot min category percentage value in live to bet: ", this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET)
        console.log("Bot min average prediction model in live to bet: ", this.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET)
        console.log("stopLoss: ", this.stopLoss)
        console.log("takeProfit: ", this.takeProfit)
        console.log("Bot strategies count: ", this.STRATEGIES.length)
    }

    protected validateBetAmount(amount: number): number{
        // if amount < minimumBet, set amount = minimumBet
        let finalAmount = Math.max(amount, this.minimumBet)
        // get the min amount between amount, maximumBet and balance
        finalAmount = Math.min(amount, this.maximumBet, this.balance)
        finalAmount = roundNumber(amount, 0)
        if(this.amountMultiple){
            finalAmount = formatNumberToMultiple(amount, this.amountMultiple)
        }
        return finalAmount
    }

    protected getStrategy(numberOfBets: number): BotStrategy|undefined{
        let profit = this.getProfitPercent()
        let strategies = this.STRATEGIES.filter((s)=>
            numberOfBets >= s.numberOfBets && profit >= s.profitPercentage
        )
        return strategies.length > 0? strategies.slice(-1)[0]: undefined
    }

    protected addLoss(amount: number){
        this.amountsLost.push(amount)
    }

    protected removeLoss(amount: number){
        let totalLoss = amount
        for(let i = this.amountsLost.length - 1; i >= 0; i--){
            if(this.amountsLost[i] > totalLoss){
                this.amountsLost[i] -= totalLoss
                break
            }
            totalLoss -= this.amountsLost[i]
            this.amountsLost.pop()
        }
    }

    protected getMinLostAmount(): number{
        // return the min amount lost (the profit must be lower than 0)
        return Math.min(...this.amountsLost)
    }

    setMaxAmountToBet(amount: number){
        this._maxAmountToBet = roundNumber(amount, 0)
        if(this._maxAmountToBet > this.balance){
            console.log("maxAmountToBet is greater than balance(", this.balance, ")")
            console.log("setting maxAmountToBet to balance")
            this._maxAmountToBet = 0
        }
        this._minAmountToBet = roundNumber(this._maxAmountToBet / 3, 0)
        if(this.amountMultiple){
            this._maxAmountToBet = formatNumberToMultiple(this._maxAmountToBet, this.amountMultiple)
            this._minAmountToBet = formatNumberToMultiple(this._minAmountToBet, this.amountMultiple)
        }
        console.log("max bet amount: ", this._maxAmountToBet)
        console.log("min bet amount: ", this._minAmountToBet)
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
    
    protected getNumberOfBets(): number{
        /*
        * number of maximum bets that the bot can hold
        * @return {number} the number of bets
        */
        return Math.floor(this.balance / this.maximumBet)
    }

    getProfit(): number{
        return roundNumber(this.balance - this.initialBalance, 2)
    }

    getProfitPercent(): number{
        return this.getProfit() / this.initialBalance
    }

    protected inStopLoss(): boolean{
        const profit = this.getProfit()
        return profit < 0 && Math.abs(profit) >= this.stopLoss
    }
    
    protected inTakeProfit(): boolean{
        const profit = this.getProfit()
        return profit >= this.takeProfit
    }

    updateBalance(balance: number){
        this.balance = balance
    }

    protected getPredictionData(prediction: PredictionCore): PredictionData{
        const categoryPrecentage = prediction.getCategoryPercentage()
        const categoryPercentageValueInLive = prediction.geCategoryPercentageValueInLive()
        const averagePredictionsOfModel = prediction.averagePredictionsOfModel
        const inCategoryPercentageValueInLive = categoryPercentageValueInLive >= this.MIN_CATEGORY_PERCENTAGE_VALUE_IN_LIVE_TO_BET
        const inCategoryPrecentage = categoryPrecentage >= this.MIN_CATEGORY_PERCENTAGE_TO_BET
        const inAveragePredictionsOfModel = averagePredictionsOfModel >= this.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET
        const predictionData = new PredictionData(
            prediction.getPredictionRoundValue(),
            prediction.getPreditionValue(),
            categoryPrecentage,
            categoryPercentageValueInLive,
            averagePredictionsOfModel,
            inCategoryPrecentage,
            inCategoryPercentageValueInLive,
            inAveragePredictionsOfModel
        )
        return predictionData
    }

    protected calculateRecoveryAmount(amountLost: number, multiplier: number): number {
        /*
        * calculate the amount to recover the losses
        * @param {number} profit the profit of bot
        * @param {number} multiplier the multiplier
        * @return {number} the amount to recover the losses
        */
        return Math.abs(amountLost) / (multiplier - 1);
    }

    protected getBetRecoveryAmount(multiplier: number, probability: number, strategy: BotStrategy): number{
        /*
        * adjust the bet recovery amount
        * @param {number} amount the amount to recover the losses
        * @param {number} multiplier the multiplier
        */
        const profit = this.getProfit()
        const minBet = this.balance * strategy.minAmountPercentageToBet
        const amountToRecoverLosses = this.calculateRecoveryAmount(profit, multiplier)
        // calculate the amount to bet to recover last amount loss
        const lastAmountLosse = this.calculateRecoveryAmount(this.getMinLostAmount(), multiplier)
        // calculates the maximum amount allowed to recover in a single bet 
        const maxRecoveryAmount = this.maximumBet * 0.5 // 50% of maximum bet (this can be a parameter of the bot)
        let amount = Math.min(amountToRecoverLosses, maxRecoveryAmount, this.balance)
        amount = amount >= maxRecoveryAmount ? lastAmountLosse : amount
        const kellyAmount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
        return Math.max(amount, kellyAmount, minBet)
    }

    generateRecoveryBets(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        const bets: Bet[] = []
        const profit = this.getProfit()
        if(profit >= 0 || multiplier < this.MIN_MULTIPLIER_TO_RECOVER_LOSSES){
            return []
        }
        let amount = this.getBetRecoveryAmount(multiplier, probability, strategy)
        amount = this.validateBetAmount(amount)
        if(multiplier >= 2){
            amount = roundNumber(amount / 1.5, 0)
            if(this.amountMultiple){
                amount = formatNumberToMultiple(amount, this.amountMultiple)
            }
            const multiplier1 = roundNumber((multiplier / 2) * 1.5, 2)
            bets.push(new Bet(amount, multiplier1))
            bets.push(new Bet(amount, multiplier1))
        }else{
            bets.push(new Bet(amount, multiplier))
        }
        return bets.filter((b)=> b.amount > 0)
    }

    protected calculateAmountBet(
        multiplier: number, 
        probability: number,
        strategy: BotStrategy, 
        usedAmount?: number
    ): number{
        usedAmount = usedAmount || 0
        let profit = this.getProfit()
        const balance = this.initialBalance - usedAmount
        if(balance <= 0){
            return 0
        }
        let minBet = balance * (strategy.minAmountPercentageToBet)
        // the balance is too high
        if(minBet > this.maximumBet){
            minBet = this.maximumBet * 0.2
        }
        let amount = 0
        if(usedAmount == 0){
            amount = minBet + profit * (strategy.profitPercentageToBet)
        }else{
            amount = usedAmount / 3
        }
        amount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
        if(amount > 0){
            amount = this.validateBetAmount(amount)
        }
        return amount
    }

    protected generateBets(
        predictionData: PredictionData,
        strategy: BotStrategy,
    ): Bet[]{
        this.bets = []
        const profit = this.getProfit()
        const categoryPrecentage = predictionData.categoryPrecentage
        const predictionRound = predictionData.predictionRound
        const predictionValue = predictionData.predictionValue
        let amount: number = 0
        let multiplier: number = 0
        if(profit < 0){
            let multiplier = predictionRound == 1? predictionValue: 2
            this.bets = this.generateRecoveryBets(multiplier, categoryPrecentage, strategy)
            return this.bets
        }
        if(predictionRound == 1){
            amount = this.calculateAmountBet(predictionValue, categoryPrecentage, strategy)
            this.bets.push(new Bet(amount, predictionValue))
        }
        else{
            // to categories 2 and 3
            amount = this.calculateAmountBet(1.95, categoryPrecentage, strategy)
            this.bets.push(new Bet(amount, 1.95))
            multiplier = generateRandomMultiplier(2, 3)
            const amount_2 = this.calculateAmountBet(multiplier, categoryPrecentage, strategy, amount)
            this.bets.push(new Bet(amount_2, multiplier))
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
        const predictionData = this.getPredictionData(prediction)
        console.log("\n\nprofit: ", profit)
        predictionData.printData()
        if(this.inStopLoss()){
            console.log("player :: Stop loss reached")
            return []
        }
        if(this.inTakeProfit()){
            console.log("player :: Take profit reached")
            return []
        }
        if(!predictionData.inCategoryPrecentage){
            return []
        }
        if(!predictionData.inAveragePredictionsOfModel){
            return []
        }
        if(predictionData.predictionValue < this.MIN_MULTIPLIER_TO_BET){
            console.log("Bot :: Prediction value is too low")
            return []
        }
        // CATEGORY 1
        if(predictionData.predictionRound == 1){
            if(!predictionData.inCategoryPercentageValueInLive){
                return []
            }
            return this.generateBets(predictionData, strategy)
        }
        // CATEGORY 2 and 3
        return this.generateBets(predictionData, strategy)
    }
}