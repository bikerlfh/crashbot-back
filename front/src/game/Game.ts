import {Multiplier, Average, Player, Bet} from "./core"

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
    }

    evaluateBets(multiplier: number){
        if(this.bets.length == 0){
            return
        }
        this.bets.forEach(bet=>{
            const profit = bet.evaluate(multiplier)
            this.balance += profit
            this.historyBets.push(bet)
        })
        this.bets = []
        console.log("Balance: ", this.balance)
    }

    addMultiplier(multiplier: number){
        this.multipliers.push(new Multiplier(multiplier))
        this.evaluateBets(multiplier)
    }
    
    /* 
    getAverage(
        category: number,
        numLastMultiplier: number|null = null
    ): number{
        let games = this.multipliers
        if(numLastMultiplier != null){
            games = this.multipliers.slice(numLastMultiplier * -1)
        }
        const multipliers: number[] = []
        games.forEach(game => {
            if(game.category == category){
                multipliers.push(game.multiplier)
            }
        })
        let average = multipliers.reduce((a, b) => a + b) / multipliers.length
        average =  parseFloat(average.toFixed(2))
        console.log("average (", category, "):", average)
        return average
    }
    */

    getLastMultipliers(numLastMultiplier: number): Multiplier[]{
        return this.multipliers.slice(numLastMultiplier * -1)
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
        const profit = this.balance - this.initialBalance
        const lenAverage = betsAverage.length
        betsAverage.forEach(average => {
            if(profit > 0 && average == 2){
                amounts.push()
            }
        })
    }

    getNextBet(): Bet[]{
        this.bets = []
        const averages = this.getTotalAverage(10)
        const averageCat_1 = averages.find(item => item.category == 1) || new Average(1)
        const averageCat_2 = averages.find(item => item.category == 2) || new Average(2)
        const averageCat_3 = averages.find(item => item.category == 3) || new Average(3)

        if(averageCat_1.count < (averageCat_2.count + averageCat_3.count)){
            this.bets.push(new Bet(2, 2))
            this.bets.push(new Bet(1, averageCat_2.average))
        }else if(averageCat_1.percentage < 60){
            this.bets.push(new Bet(2, averageCat_1.average))
        }
        return this.bets
    } 
}
