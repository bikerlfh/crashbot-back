

export class Player{
    private MIN_NUMBER_OF_BETS: number = 0
    private MIN_BET_PERCENTAGE_OF_BALANCE: number = 0.003
    private MAX_BET_PERCENTAGE_OF_BALANCE: number = 0.008
    private STOP_LOSS_PERCENTAGE: number = 0
    private TAKE_PROFIT_PERCENTAGE: number = 0
    private PROFIT_STRATEGIES: [] = []
    
    private initialBalance: number
    private balance: number
    private stopLoss: number;
    private takeProfit: number;
    private minimumBet: number
    private maximumBet: number
    private _minBet: number = 0
    private _maxBet: number = 0

    constructor(
        balance: number, 
        minimumBet: number = 0,
        maximumBet: number = 0
    ){
        if(this.MIN_NUMBER_OF_BETS == 0){
            throw new Error("NUMBER_OF_BETS must be greater than 0")
        }
        if(this.STOP_LOSS_PERCENTAGE == 0){
            throw new Error("STOP_LOSS_PERCENTAGE must be greater than 0")
        }
        if(this.TAKE_PROFIT_PERCENTAGE == 0){
            throw new Error("TAKE_PROFIT_PERCENTAGE must be greater than 0")
        }
        this.initialBalance = balance
        this.balance = balance
        this.minimumBet = minimumBet
        this.maximumBet = maximumBet
        this.stopLoss = this.balance * (this.STOP_LOSS_PERCENTAGE / 100)
        this.takeProfit = this.balance * (this.TAKE_PROFIT_PERCENTAGE / 100)
        this.calculateMinMaxBet()
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
        return amount
    }

    getProfit(): number{
        return this.balance - this.initialBalance
    }

    getProfitPercent(): number{
        return this.getProfit() / this.initialBalance * 100
    }

    private calculateMinMaxBet(){
        const numMinBets = this.balance / this.minimumBet
        if(numMinBets <= 50){
            // if the balance is less than 50 minimum bets, the minimum bet is the minimum bet
            // and the maximum bet is 3 times the minimum bet
            this._minBet = this.minimumBet
            this._maxBet = parseFloat((this.minimumBet * (numMinBets * this.MIN_NUMBER_OF_BETS)).toFixed(0))
        }else{
            // if the balance is more than 50 minimum bets, the minimum bet is 0.3% of the balance
            this._minBet = parseFloat((this.balance *  this.MIN_BET_PERCENTAGE_OF_BALANCE).toFixed(0))
            // and the maximum bet is 0.8% of the balance
            this._maxBet = parseFloat((this.balance *  this.MAX_BET_PERCENTAGE_OF_BALANCE).toFixed(0))
        }
        this._minBet = this.validateBetAmount(this._minBet)
        this._maxBet = this.validateBetAmount(this._maxBet)
    }

    calculateAmountBet(multiplier: number, usedAmount?: number): number{
        usedAmount = usedAmount || 0
        let balance = this.balance - usedAmount
        let profit = this.getProfit()
        let amount = this._minBet
        if(profit < 0){
            amount = (Math.abs(profit) / (multiplier -1)) + this._minBet
        }
        else{
            amount *= 2
        }
        amount = this.validateBetAmount(amount)
        if(amount > balance){
            amount = balance
        }
        amount = parseFloat(amount.toFixed(0))
        return amount
    }
}


export class TightPlayer extends Player{
    
}

export class LoosePlayer extends Player{
    
}

export class AggressivePlayer extends Player{
    
}