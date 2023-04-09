

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


export type BotStrategy = {
    numberOfBets: number
    profitPercentage: number
    minAmountPercentageToBet: number
    profitPercentageToBet: number
    others: number
}

export class Bot{
    id: number
    botType: string
    riskFactor: number
    minMultiplierToBet: number
    minMultiplierToRecoverLosses: number
    minCategoryPercentageToBet: number
    minCategoryPercentageValueInLiveToBet: number
    minAveragePredictionModelInLiveToBet: number
    stopLossPercentage: number
    takeProfitPercentage: number
    strategies: BotStrategy[]

    constructor(object: any){
        this.id = object.id
        this.botType = object.bot_type
        this.riskFactor = object.risk_factor
        this.minMultiplierToBet = object.min_multiplier_to_bet
        this.minCategoryPercentageToBet = object.min_category_percentage_to_bet
        this.minMultiplierToRecoverLosses = object.min_multiplier_to_recover_losses
        this.minCategoryPercentageValueInLiveToBet = object.min_category_percentage_value_in_live_to_bet
        this.minAveragePredictionModelInLiveToBet = object.min_average_prediction_model_in_live_to_bet
        this.stopLossPercentage = object.stop_loss_percentage
        this.takeProfitPercentage = object.take_profit_percentage
        this.strategies = object.strategies.map((strategy: any) => ({
            numberOfBets: strategy.number_of_bets,
            profitPercentage: strategy.profit_percentage,
            minAmountPercentageToBet: strategy.min_amount_percentage_to_bet,
            profitPercentageToBet: strategy.profit_percentage_to_bet,
            others: strategy.others
        }))
    }
}
