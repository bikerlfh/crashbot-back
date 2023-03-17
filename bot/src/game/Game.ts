import {Multiplier, Average, Player, Bet} from "./core"
import {AviatorBotAPI} from "../api/AviatorBotAPI"
import { HomeBet } from "../constants"
import { PredictionModel, PredictionCore } from "./PredictionCore"

export class Game {
    homeBet: HomeBet
    balance: number
    initialBalance: number
    multipliers: Multiplier[] = []
    bets: Bet[] = []
    historyBets: Bet[] = []
    minimumBet: number = 0
    maximumBet: number = 0
    maximumWinForOneBet: number = 0
    _minBet: number = 0
    _maxBet: number = 0
    _prediction_model: PredictionModel
    
    constructor(
        homeBet: HomeBet,
        multipliers: number[] = [],
        balance: number
    ){
        this.homeBet = homeBet
        multipliers.forEach(item => {
            this.multipliers.push(new Multiplier(item))
        })
        this.balance = balance
        this.initialBalance = balance
        this.minimumBet = homeBet.minBet
        this.maximumBet = homeBet.maxBet
        this.maximumWinForOneBet = this.maximumBet * 100
        this._prediction_model = PredictionModel.getInstance()
        this.calculateMinMaxBet()
        this.requestSaveMultipliers(multipliers)
    }

    private requestSaveMultipliers(multipliers: number[]){
        AviatorBotAPI.requestSaveMultipliers(this.homeBet.id, multipliers).catch(
            error => {
                console.error("error in requestSaveMultipliers:", error)
            }
        )
    }

    private async getPrediction(): Promise<PredictionCore|null>{
        // const multipliers = this.multipliers.map(item => item.multiplier)
        const predictions = await AviatorBotAPI.requestPrediction(this.homeBet.id).then(
            response => {
                console.log("response in requestPrediction:", response)
                return response
            }
        ).catch(error => { return [] })
        if(predictions.length == 0){
            this._prediction_model.addPredictions(predictions)
            return null
        }
        this._prediction_model.addPredictions(predictions)
        return this._prediction_model.getBestPrediction()
    }

    calculateMinMaxBet(){
        const numMinBets = this.balance / this.minimumBet
        if(numMinBets <= 50){
            this._minBet = this.minimumBet
            this._maxBet = parseFloat((this.minimumBet * (numMinBets * 3)).toFixed(0))
            return
        }
        this._minBet = parseFloat((this.minimumBet * (numMinBets * 0.003)).toFixed(0))
        this._maxBet = parseFloat((this.minimumBet * (numMinBets * 0.008)).toFixed(0))
    }

    evaluateBets(multiplier: number){
        if(this.bets.length == 0){
            return
        }
        this.bets.forEach(bet=>{
            const profit = bet.evaluate(multiplier)
            this.balance += profit
            // this.historyBets.push(bet)
        })
        this.bets = []
    }

    addMultiplier(multiplier: number){
        this._prediction_model.addMultiplierResult(multiplier)
        this.evaluateBets(multiplier)
        this.multipliers.push(new Multiplier(multiplier))
        this.requestSaveMultipliers([multiplier])
    }

    // return an array with categories
    getPositionCategories(averages: Average[]){
        const result: number[] = []
        averages.forEach(average => {
            result.push(average.category)
        })
        return result
    }

    getTotalAverage(numLastMultiplier: number): Average[]{
        let result: Average[] = []
        let games = this.multipliers.slice(numLastMultiplier * -1).reverse()
        games.forEach(item => {
            const average = result.find(a => a.category == item.category) || new Average(
                item.category
            )
            average.totalMultiplier += item.multiplier
            average.count += 1
            average.average = average.totalMultiplier / average.count
            average.average = parseFloat(average.average.toFixed(2))
            average.totalMultiplier =  parseFloat(average.totalMultiplier.toFixed(2))
            average.percentage = average.count * numLastMultiplier / 100
            average.positions.push(games.indexOf(item))
            const index = result.indexOf(average)
            if(index < 0){
                result.push(average)
            }
        })
        return result
    }
    /*calculateAmountBet(betsAverage: number[]){
        const amounts: number[] = []
        let profit = this.balance - this.initialBalance
        let balance = this.balance
        betsAverage.forEach(average => {
            let amount = this._minBet
            if(profit < 0){
                amount = (Math.abs(profit) / (average -1))
            }else if(amounts.length > 0){
                amount = amounts.slice(-1)[0] / 3
            }
            amount = amount > this.minimumBet? amount: this.minimumBet;
            if(amount > balance){
                amount = balance
            }
            if(amount > this.maximumBet){
                amount = this.maximumBet
            }
            amount = parseFloat(amount.toFixed(0))
            balance -= amount
            amounts.push(amount)
        })
        return amounts
    }*/
    private _randomMultiplier(min: number, max: number): number{
        const precision = 100;
        const randomNum = Math.floor(
            Math.random() * (max * precision - min * precision) + 1 * precision
        ) / (min * precision);
        return randomNum
        // return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    calculateAmountBet(multiplier: number, usedAmount?: number): number{
        if(!usedAmount){
            usedAmount = 0
        }
        let balance = this.balance - usedAmount
        let profit = balance - this.initialBalance
        let amount = this._minBet
        console.log("balance: ", balance, "; profit: ", profit, "; amount: ", amount)
        if(profit < 0){
            amount = (Math.abs(profit) / (multiplier -1)) + this.minimumBet
        }
        else{
            amount *= 2
        }
        amount = amount > this.minimumBet? amount: this.minimumBet;
        if(amount > balance){
            amount = balance
        }
        if(amount > this.maximumBet){
            amount = this.maximumBet
        }
        if(amount < 0){
            amount = this._minBet
        }
        amount = parseFloat(amount.toFixed(0))
        return amount
    }

    async getNextBet(): Promise<Bet[]>{
        const prediction = await this.getPrediction()
        if(prediction == null){
            console.log("prediction is null")
            return []
        }
        console.log("prediction selected: ", prediction)
        console.log("prediction selected: ", prediction.getPredictionRoundValue())
        this.bets = []
        const numLastMultiplier = 15
        const averages = this.getTotalAverage(numLastMultiplier)
        const positionCategories = this.getPositionCategories(averages)
        const averageCat_1 = averages.find(item => item.category == 1) || new Average(1)
        const averageCat_2 = averages.find(item => item.category == 2) || new Average(2)
        const averageCat_3 = averages.find(item => item.category == 3) || new Average(3)
        const percentage = ((averageCat_2.count + averageCat_3.count) / numLastMultiplier) * 100
        const percentageCat1 = 100 - percentage
        const profit = this.balance - this.initialBalance

        const averages_per = {
            1: averageCat_1.percentage,
            2: averageCat_2.percentage,
            3: averageCat_3.percentage
        }
        console.log("averages: ", averages_per, "; percentage:", percentage.toFixed(2))
        // no bets when prediction is 1
        const categoryPrecentage = prediction.getCategoryPercentage()
        const predictionRound = prediction.getPredictionRoundValue()
        let predictionValue = prediction.getPreditionValue()
        const averagePredictionValuesInLive = prediction.averagePredictionValuesInLive
        const averagePredictionInLive = prediction.averagePredictionInLive
        if(predictionValue < 0){
            predictionValue = 1.1
        }
        if(predictionRound == 1){
            if(averagePredictionValuesInLive < 70){
                console.log("predictionRound == 1 && averagePredictionValuesInLive < 70")
                return []
            }
            this.bets.push(new Bet(this.calculateAmountBet(predictionValue), predictionValue))
            return this.bets
        }
        if(predictionRound == 2){
            if(averagePredictionInLive < 70){
                if(profit < 0){
                    console.log("predictionRound == 2 && averagePredictionInLive < 70")
                    return []
                }
                this.bets.push(new Bet(this.calculateAmountBet(predictionValue), predictionValue)) 
                return this.bets
            }
            if(profit < 0){
                this.bets.push(new Bet(this.calculateAmountBet(predictionRound), predictionRound))
            }else{
                const amount = this.calculateAmountBet(1.95)
                this.bets.push(new Bet(amount, 1.95))
                const amount2 = parseFloat((amount / 3).toFixed(2))
                this.bets.push(new Bet(amount2, this._randomMultiplier(2, 3)))
            }
            return this.bets
        }    
        if(averagePredictionInLive < 70){
            if(profit > 0){
                this.bets.push(new Bet(this.calculateAmountBet(predictionRound), predictionRound))
                return this.bets
            }
            return []
        }
        const amount = this.calculateAmountBet(1.95)
        this.bets.push(new Bet(amount, 1.95))
        if(profit > 0){
            const amount2 = parseFloat((amount / 3).toFixed(2))
            this.bets.push(new Bet(amount2, 1.95))
        }
        return this.bets
    }
}
