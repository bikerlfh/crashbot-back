

export class Prediction{
    id: number
    prediction: number
    predictionRound: number
    averagePredictions: number
    categoryPercentage: number

    constructor(object: any){
        this.id = object.id
        this.prediction = object.prediction
        this.predictionRound = object.prediction_round
        this.averagePredictions = object.average_predictions
        this.categoryPercentage = object.category_percentage
    }
}



export class BetData{
    constructor(
        public externalId: string, 
        public prediction: number, 
        public multiplier: number, 
        public amount: number,
        public multiplierResult?: number, 
    ){}

    toDict(){
        return {
            external_id: this.externalId,
            prediction: this.prediction,
            multiplier: this.multiplier,
            multiplier_result: this.multiplierResult,
            amount: this.amount
        }
    }
}

export class PlayerStrategy{
    id: number
    strategyType: string
    numberOfBets: number
    profitPercentage: number
    // minBalancePercentageToBetAmount: the percentage of the balance to create the bet amount
    minBalancePercentageToBetAmount: number
    // profitPercentageToBetAmount: the percentage of the profit to create the bet amount
    profitPercentageToBetAmount: number
    others?: any

    constructor(object: any){
        this.id = object.id
        this.strategyType = object.strategy_type
        this.numberOfBets = object.number_of_bets
        this.profitPercentage = object.profit_percentage
        this.minBalancePercentageToBetAmount = object.min_balance_percentage_to_bet_amount
        this.profitPercentageToBetAmount = object.profit_percentage_to_bet_amount
        this.others = object.others
    }
}
