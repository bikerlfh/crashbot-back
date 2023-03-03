import {Multiplier, Average, Player, Bet} from "./core"
import {AviatorBotAPI} from "../api/AviatorBotAPI"


export class Game {
    betHome: string = ""
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
    
    constructor(
        betHome: string,
        multipliers: number[] = [],
        balance: number,
        minimumBet: number,
        maximumBet: number,
        maximumWinForOneBet: number
    ){
        this.betHome = betHome
        multipliers.forEach(item => {
            this.addMultiplier(item)
        })
        this.balance = balance
        this.initialBalance = balance
        this.minimumBet = minimumBet
        this.maximumBet = maximumBet
        this.maximumWinForOneBet = maximumWinForOneBet
        this.calculateMinMaxBet()
        // AviatorBotAPI.save_multipliers(1, multipliers)
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
        this.evaluateBets(multiplier)
        this.multipliers.push(new Multiplier(multiplier))
    }

    getTotalAverage(numLastMultiplier: number): Average[]{
        let result: Average[] = []
        let games = this.multipliers.slice(numLastMultiplier * -1)
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
    calculateAmountBet(betsAverage: number[]){
        const amounts: number[] = []
        let profit = this.balance - this.initialBalance
        betsAverage.forEach(average => {
            let amount = this._minBet
            if(profit < 0){
                amount = (Math.abs(profit) / (average -1))
                // console.log("PROFIT NEGATIVE: profit:", profit, "; average: ", average, "; amount: ", amount)
            }else if(amounts.length > 0){
                amount = this._minBet / 3
            }
            amount = amount > this.minimumBet? amount: this.minimumBet;
            if(amount > this.balance){
                amount = this.balance
            }
            amount = parseFloat(amount.toFixed(0))
            amounts.push(amount)
        })
        return amounts
    }
    
    _randomMultiplier(min: number, max: number): number{
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    getNextBet(): Bet[]{
        this.bets = []
        const numLastMultiplier = 10
        const averages = this.getTotalAverage(numLastMultiplier)
        const averageCat_1 = averages.find(item => item.category == 1) || new Average(1)
        const averageCat_2 = averages.find(item => item.category == 2) || new Average(2)
        const averageCat_3 = averages.find(item => item.category == 3) || new Average(3)
        const percentage = ((averageCat_2.count + averageCat_3.count) / numLastMultiplier) * 100
        const percentageCat1 = 100 - percentage
        const profit = this.balance - this.initialBalance
        console.log("getNextBet: percentage: ", percentage)
        let amounts: number[] = []
        if(percentage >= 60 && profit > 0){
            this.bets.push(new Bet(profit, 2))
        }else if(percentage >= 50){
            if(profit >0){
                const multiplier_2 = this._randomMultiplier(2, 5)
                amounts = this.calculateAmountBet([2])
                const amount2 = parseFloat((amounts[0]/3).toFixed(0))
                this.bets.push(new Bet(amounts[0], 2))
                this.bets.push(new Bet(amount2, multiplier_2))
            }else{
                amounts = this.calculateAmountBet([2])
                this.bets.push(new Bet(amounts[0], 2))
            }
        }else if(percentage >= 40 && profit >= 0){
            amounts = this.calculateAmountBet([2])
            this.bets.push(new Bet(amounts[0], 2))
        }else if(profit > 0){
            amounts = this.calculateAmountBet([averageCat_1.average])
            this.bets.push(new Bet(amounts[0], averageCat_1.average))
        }else if(percentageCat1 >= 90){
            const amount = parseFloat((this.balance * 0.3).toFixed(0))
            this.bets.push(new Bet(amount, 1.95))
        }
        return this.bets
    } 
}
