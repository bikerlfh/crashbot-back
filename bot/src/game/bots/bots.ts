import { BotStrategy } from "../../api/models"
import { PredictionCore } from "../PredictionCore"
import { Bet, PredictionData } from "../core"
import { BotType } from "../core"
import { adaptiveKellyFormula } from "../utils"
import { BotBase } from "./base"
import {sendEventToGUI} from "../../ws/gui_events"


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

    setMaxAmountToBet(amount: number){
        sendEventToGUI.log.info("this bot not allowed to set maxAmountToBet.")
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
    private _initialBalance = 0

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

    async initialize(balance: number){
        sendEventToGUI.log.debug("initializing bot static")
        await super.initialize(balance)
        this._initialBalance = balance
        this.setMaxAmountToBet((global as any).maxAmountToBet)
    }
    
    // NOTE: remove this method when the bot not need recover all profits
    /*updateBalance(balance: number){
        if(balance > this.initialBalance){
            this.initialBalance = balance
        }
        super.updateBalance(balance)
    }*/

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
        if(amountToRecoverLosses < this.minimumBet){
            sendEventToGUI.log.debug(
                `getBetRecoveryAmount :: amountToRecoverLosses <= this.minimumBet 
                (${amountToRecoverLosses} <= ${this.minimumBet})`
            )
            return this.minimumBet
        }
        // calculate the amount to bet to recover last amount loss
        const lastAmountLosse = this.calculateRecoveryAmount(this.getMinLostAmount(), multiplier)
        // calculates the maximum amount allowed to recover in a single bet 
        const maxRecoveryAmount = this.maximumBet * 0.3 // 30% of maximum bet (this can be a parameter of the bot)
        let amount = Math.min(amountToRecoverLosses, maxRecoveryAmount, this.balance)
        amount = amount >= maxRecoveryAmount ? lastAmountLosse : amount
        amount =  Math.max(amount, this.minimumBet)
        // validation of new balance after bet recovery with the stop loss
        const posibleLoss = Math.abs(profit) + amount
        if(posibleLoss >= this.stopLoss){
            amount = Math.min(Math.floor(amount * 0.3), lastAmountLosse)
            sendEventToGUI.log.debug(
                `getBetRecoveryAmount :: posibleLoss >= this.stopLoss 
                (${posibleLoss} >= ${this.stopLoss}) :: new amount=${amount}`
            )
        }
        // const kellyAmount = adaptiveKellyFormula(multiplier, probability, this.RISK_FACTOR, amount)
        amount =  Math.max(amount, this.minimumBet)
        sendEventToGUI.log.debug(`BotStatic :: getBetRecoveryAmount ${amount}`)
        return amount
    }

    generateRecoveryBets(multiplier: number, probability: number, strategy: BotStrategy): Bet[]{
        if(multiplier < this.MIN_MULTIPLIER_TO_RECOVER_LOSSES){
            sendEventToGUI.log.warning(
                `multiplier is less than ${this.MIN_MULTIPLIER_TO_RECOVER_LOSSES}, 
                no recovery bets`
            )
            return []
        }
        sendEventToGUI.log.debug(`Amount Lost: ${this.amountsLost}`)
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
            sendEventToGUI.log.debug("generateBets :: profit < 0")
            // always the multiplier to recover losses is 1.95
            this.bets = this.generateRecoveryBets(
                this.MIN_MULTIPLIER_TO_RECOVER_LOSSES, 
                categoryPrecentage,
                strategy
            )
            return this.bets
        }
        // to category 2
        // if the profit is greater than 10% of the initial balance
        const profitPercentage = this.getProfitPercent()
        if(profitPercentage > 0.10){
            sendEventToGUI.log.debug("generateBets :: profitPercentage > 0.10")
            const maxBetKellyAmount = adaptiveKellyFormula(1.95, categoryPrecentage, this.RISK_FACTOR, this._maxAmountToBet)
            const minBetKellyAmount = adaptiveKellyFormula(2, categoryPrecentage, this.RISK_FACTOR, this._minAmountToBet)
            this.bets.push(new Bet(Math.max(maxBetKellyAmount, this._maxAmountToBet), 1.95))
            this.bets.push(new Bet(Math.max(minBetKellyAmount, this._minAmountToBet), 2))
        }else{
            this.bets.push(new Bet(this._maxAmountToBet, 1.95))
            this.bets.push(new Bet(this._minAmountToBet, 2))
        }
        this.bets = this.bets.filter((b)=> b.amount > 0)
        return this.bets
    }

    getNextBet(prediction: PredictionCore): Bet[]{
        if(prediction == null){
            return []
        }
        const profit = this.getProfit()
        if(profit >= 0){
            this.resetLosses()
        }
        const predictionData = this.getPredictionData(prediction)
        const numberOfBet = this.getNumberOfBets()
        const strategy = this.getStrategy(numberOfBet)
        if(!strategy){
            sendEventToGUI.log.warning(
                "No strategy found for profit percentage: " + this.getProfitPercent()
            )
            return []
        }
        sendEventToGUI.log.debug("profit: " + profit)
        predictionData.printData()
        if(this.inStopLoss()){
            sendEventToGUI.log.warning("Stop loss reached")
            return []
        }
        if(this.inTakeProfit()){
            sendEventToGUI.log.success("Take profit reached")
            return []
        }
        if(!predictionData.inCategoryPrecentage){
            sendEventToGUI.log.warning("Prediction value is not in category precentage")
            return []
        }
        if(predictionData.predictionValue < this.MIN_MULTIPLIER_TO_BET){
            sendEventToGUI.log.warning("Prediction value is too low")
            return []
        }
        // CATEGORY 1 not bet
        if(predictionData.predictionRound == 1){
            sendEventToGUI.log.warning("Prediction round is 1")
            return []
        }
        // CATEGORY 2
        return this.generateBets(predictionData, strategy)
    }
}