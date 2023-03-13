

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

