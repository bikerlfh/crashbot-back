import { BotStrategy } from "../../api/models"
import { PredictionCore } from "../PredictionCore"
import { Bet, PredictionData } from "../core"
import { BotType } from "../core"
import { adaptiveKellyFormula, formatNumberToMultiple } from "../utils"
import { BotBase } from "./base"
import {roundNumber} from "../utils"
import { count } from "console"



export class Bot extends BotBase{
    /*
    * The Bot class is a class used to determine the optimal fraction of one's capital to bet on a given bet. 
    */
    constructor(
        botType: BotType,
        minimumBet: number = 0,
        maximumBet: number = 0,
        amountMultiple?: number
    ){
        super(botType, minimumBet, maximumBet, amountMultiple)
    }

    async initialize(balance: number){
        await super.initialize(balance)
    }

    getBetRecoveryAmount(multiplier: number, probability: number, strategy: BotStrategy): number{
        return super.getBetRecoveryAmount(multiplier, probability, strategy)
    }

    generateRecoveryBets(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        return super.generateRecoveryBets(multiplier, probability, strategy)
    }

    calculateAmountBet(
        multiplier: number, 
        probability: number,
        strategy: BotStrategy, 
        usedAmount?: number
    ): number{
        return super.calculateAmountBet(multiplier, probability, strategy, usedAmount)
    }

    generateBets(
        predictionData: PredictionData,
        strategy: BotStrategy,
    ): Bet[]{
        return super.generateBets(predictionData, strategy)
    }

    getNextBet(prediction: PredictionCore): Bet[]{
       return super.getNextBet(prediction)
    }
}


export class BotStatic extends BotBase{
    /*
    * The BotStatic class is a class used to determine the optimal fraction of one's capital to bet on a given bet.
    * this Bot is use to bet in the game, it's necesary that the custormer select the two amonunt to bet (max and min)
    * in the control 1 the bot will bet the max amount of money that the customer select 
    * in the control 2 the bot will bet the min amount of money that the customer select
    * the min amount of bet should be less than the max amount of bet / 3 example: max bet = 300, min bet = 300/3 = 100
    */
    private _maxBetAmount: number = 0
    private _minBetAmount: number = 0

    constructor(
        botType: BotType,
        minimumBet: number = 0,
        maximumBet: number = 0,
        amountMultiple?: number
    ){
        /*
        * @param botType: BotType bot type
        * @param minimumBet: number minimum bet allowed by home bet
        * @param maximumBet: number maximum bet allowed by home bet
        * @param minBetAmount: number minimum bet amount allowed by customer
        * @param maxBetAmount: number maximum bet amount allowed by customer
        * @param amountMultiple?: number
        */
        super(botType, minimumBet, maximumBet, amountMultiple)
    }

    async initialize(balance: number, autoPlay?: boolean){
        autoPlay = autoPlay || false
        console.log("initializing bot static")
        await super.initialize(balance)
        if(!autoPlay){
            return
        }
        // add the minimum and maximum bet
        let readlineSync = require('readline-sync');
        while(this._maxBetAmount <= 0 || this._maxBetAmount > balance){
            this._maxBetAmount = parseFloat(readlineSync.question(
                "type the max amount of bet " +
                "(this amount can not be higth that the balance " + balance + "): "
            ));
        }
        this._minBetAmount = roundNumber(this._maxBetAmount / 3, 0)
        if(this.amountMultiple){
            this._maxBetAmount = formatNumberToMultiple(this._maxBetAmount, this.amountMultiple)
            this._minBetAmount = formatNumberToMultiple(this._minBetAmount, this.amountMultiple)
        }
        console.log("max bet amount: ", this._maxBetAmount)
        console.log("min bet amount: ", this._minBetAmount)
    }

    protected getBetRecoveryAmount(multiplier: number, probability: number, strategy: BotStrategy): number{
        /*
        * adjust the bet recovery amount
        * @param {number} amount the amount to recover the losses
        * @param {number} multiplier the multiplier
        */
        const profit = this.getProfit()
        // NOTE: no use minBet by strategy
        // const minBet = this.balance * strategy.minAmountPercentageToBet
        const amountToRecoverLosses = this.calculateRecoveryAmount(profit, multiplier)
        if(amountToRecoverLosses <= this.minimumBet && multiplier >= 1.95){
            return this.minimumBet
        }
        // calculate the amount to bet to recover last amount loss
        const lastAmountLosse = this.calculateRecoveryAmount(this.amountsLost.slice(-1)[0], multiplier)
        // calculates the maximum amount allowed to recover in a single bet 
        const maxRecoveryAmount = this.maximumBet * 0.5 // 50% of maximum bet (this can be a parameter of the bot)
        let amount = Math.min(amountToRecoverLosses, maxRecoveryAmount, this.balance)
        amount = amount >= maxRecoveryAmount ? lastAmountLosse : amount
        amount =  Math.max(amount, this.minimumBet)
        // validation of new balance after bet recovery with the stop loss
        const posibleLoss = Math.abs(profit) + amount
        if(posibleLoss >= this.stopLoss){
            amount = Math.min(Math.floor(amount * 0.3), lastAmountLosse)
        }
        // const kellyAmount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
        return Math.max(amount, this.minimumBet)
    }

    /*generateRecoveryBets(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        const bets: Bet[] = []
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
    }*/

    generateRecoveryBets(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        const bets: Bet[] = []
        let amount = this.getBetRecoveryAmount(multiplier, probability, strategy)
        amount = this.validateBetAmount(amount)
        bets.push(new Bet(amount, multiplier))
        return bets.filter((b)=> b.amount > 0)
    }

    generateBets(
        predictionData: PredictionData,
        strategy: BotStrategy,
    ): Bet[]{
        this.bets = []
        const profit = this.getProfit()
        const categoryPrecentage = predictionData.categoryPrecentage
        if(profit < 0){
            // always the multiplier to recover losses is 1.95
            this.bets = this.generateRecoveryBets(1.95, categoryPrecentage, strategy)
            return this.bets
        }
        // to category 2
        // if the profit is greater than 10% of the initial balance
        const profitPercentage = this.getProfitPercent()
        if(profitPercentage > 0.10){
            const maxBetKellyAmount = adaptiveKellyFormula(1.95, categoryPrecentage, this.RISK_FACTOR, this._maxBetAmount)
            const minBetKellyAmount = adaptiveKellyFormula(2, categoryPrecentage, this.RISK_FACTOR, this._minBetAmount)
            this.bets.push(new Bet(Math.max(maxBetKellyAmount, this._maxBetAmount), 1.95))
            this.bets.push(new Bet(Math.max(minBetKellyAmount, this._minBetAmount), 2))
        }else{
            this.bets.push(new Bet(this._maxBetAmount, 1.95))
            this.bets.push(new Bet(this._minBetAmount, 2))
        }
        this.bets = this.bets.filter((b)=> b.amount > 0)
        return this.bets
    }

    getNextBet(prediction: PredictionCore): Bet[]{
        if(prediction == null){
            return []
        }
        const profit = this.getProfit()
        const predictionData = this.getPredictionData(prediction)
        const numberOfBet = this.getNumberOfBets()
        const strategy = this.getStrategy(numberOfBet)
        if(!strategy){
            console.warn(
                "No strategy found for profit percentage: ", this.getProfitPercent()
            )
            return []
        }
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
        if(predictionData.predictionValue < this.MIN_MULTIPLIER_TO_BET){
            console.log("Bot :: Prediction value is too low")
            return []
        }
        // CATEGORY 1 not bet
        if(predictionData.predictionRound == 1){
            return []
        }
        // CATEGORY 2
        return this.generateBets(predictionData, strategy)
    }
}