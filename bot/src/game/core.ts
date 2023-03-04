export class Player{
    id: number|null = null
    balance: number = 0

    constructor(id: number, balance: number){
        this.id = id
        this.balance = balance
    }
    
    updateBalance(amount: number){
        // the amount can be negative
        this.balance += amount
    }
}


export class Multiplier{
    multiplier: number
    category: number
    
    constructor(multiplier: number){
        this.multiplier = multiplier
        if(multiplier < 2){
            this.category = 1
        }
        else if(multiplier < 10){
            this.category = 2
        }
        else{
            this.category = 3
        }
    }
}


export class Average{
    category: number
    average: number = 0
    totalMultiplier: number = 0
    count: number = 0
    percentage: number = 0
    positions: number[] = []

    constructor(category:number){
        this.category = category
    }
 }

 export class Bet{
    amount: number = 0
    multiplier: number = 0
    profit: number = 0

    constructor(amount: number, multiplier: number){
        this.amount = amount
        this.multiplier = multiplier
    }

    evaluate(lastMultiplier: number): number{
        if(lastMultiplier >= this.multiplier){
            this.profit += this.amount * (this.multiplier - 1)
        }else{
            this.profit -= this.amount
        }
        return parseFloat(this.profit.toFixed(2))
    }
 }