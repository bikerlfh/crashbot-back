
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


export class Game {
    betHome: string = ""
    player: Player|null
    historyGame: Multiplier[] = []
    
    constructor(
        betHome: string,
        historyGame: number[] = [],
        player: Player|null
    ){
        this.betHome = betHome;
        historyGame.forEach(item => {
            this.addMultiplier(item)
        })
        this.player = player
    }

    addMultiplier(multiplier: number){
        this.historyGame.push(new Multiplier(multiplier))
    }
    
    getAverage(
        category: number,
        num_last_games: number|null = null
    ): number{
        let games = this.historyGame
        if(num_last_games != null){
            games = this.historyGame.slice(num_last_games * -1)
        }
        const multipliers: number[] = []
        games.forEach(game => {
            if(game.category == category){
                multipliers.push(game.multiplier)
            }
        })
        let average = multipliers.reduce((a, b) => a + b) / multipliers.length
        return parseFloat(average.toFixed(2))
    }

 
}


