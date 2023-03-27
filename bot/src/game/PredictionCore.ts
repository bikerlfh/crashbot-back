import { Prediction } from "../api/models";


export class PredictionCore{
    id: number
    averagePredictionsOfModel: number
    predictionValues: number[] = []
    predictionRounds: number[] = []
    multiplierResults: number[] = []
    averagePredictionValuesInLive: number = 0
    averagePredictionInLive: number = 0
    categoryPercentages: {[key: number]: number} = {
        1: 0,
        2: 0,
        3: 0,
    }

    constructor(
        id: number,
        averagePredictions: number
    ){
        this.id = id
        this.averagePredictionsOfModel = averagePredictions
        this.averagePredictionInLive = averagePredictions
    }

    addPrediction(
        prediction: number,
        predictionRound: number,
        averagePredictions: number,
        categoryPercentage: number = 0
    ){
        this.predictionValues.push(prediction)
        this.predictionRounds.push(predictionRound)
        this.averagePredictionsOfModel = averagePredictions
        if(this.categoryPercentages[predictionRound] === 0){
            this.categoryPercentages[predictionRound] = categoryPercentage
        }
    }

    addMultiplierResult(multiplier: number){
        this.multiplierResults.push(multiplier)
        this.calculateAveragePredictions()
        this.calculateCategoryPercentages()
    }

    calculateCategoryPercentages(){
        for(let i = 1; i <= 3; i++){
            let countI = 0
            let count = 0;
            for (let j = 0; j < this.predictionRounds.length; j++){
                const value = this.predictionRounds[j]
                if(value == i){
                    countI +=1
                    if(value <= this.multiplierResults[j]){
                        count++;
                    }
                }
            }
            if(count === 0 || countI === 0){
                continue;
            }
            this.categoryPercentages[i] = (count / countI) * 100;
        }
    }

    calculateAveragePredictions(){
        let correctCount = 0;
        let correcValuesCount = 0;
        for (let i = 0; i < this.multiplierResults.length; i++) {
            if (this.predictionRounds[i] <= this.multiplierResults[i]) {
                correctCount++;
            }
            if (this.predictionValues[i] <= this.multiplierResults[i]) {
                correcValuesCount++;
            }
        }
        this.averagePredictionInLive = (correctCount / this.multiplierResults.length) * 100;
        this.averagePredictionValuesInLive = (correcValuesCount / this.multiplierResults.length) * 100;
    }

    getPreditionValue(): number{
        return this.predictionValues.slice(-1)[0]
    }

    getPredictionRoundValue(): number{
        return this.predictionRounds.slice(-1)[0]
    }

    getCategoryPercentage(): number{
        return this.categoryPercentages[this.getPredictionRoundValue()]
    }
}

export class PredictionModel{
    private static instance: PredictionModel;
    predictions: PredictionCore[] = []

    private constructor() { }

    public static getInstance(): PredictionModel {
        if (!PredictionModel.instance) {
            PredictionModel.instance = new PredictionModel();
        }
        return PredictionModel.instance;
    }

    addPredictions(predictions: Prediction[]){
        const new_predictions: PredictionCore[] = []
        predictions.forEach(prediction => {
            let prediction_ = this.predictions.find(
                item => item.id == prediction.id
            )
            if(prediction_){
                prediction_.addPrediction(
                    prediction.prediction,
                    prediction.predictionRound,
                    prediction.averagePredictions
                )
            }else{
                prediction_ = new PredictionCore(
                    prediction.id,
                    prediction.averagePredictions
                )
                prediction_.addPrediction(
                    prediction.prediction,
                    prediction.predictionRound,
                    prediction.averagePredictions,
                    prediction.categoryPercentage
                )
            }
            new_predictions.push(prediction_)
        })
        this.predictions = new_predictions
        // this.predictions = this.predictions.filter(obj => obj.id in predictions.map(item => item.id));
    }
    
    addMultiplierResult(multiplier: number){
        this.predictions.forEach(prediction => {
            if(prediction.multiplierResults.length < prediction.predictionRounds.length){
                prediction.addMultiplierResult(multiplier)
            }
        })
    }

    getBestPrediction(): PredictionCore|null{
        if(this.predictions.length == 0){
            return null
        }
        let bestPrediction = this.predictions[0]
        this.predictions.forEach(pre => {
            if(pre.averagePredictionInLive > bestPrediction.averagePredictionInLive){
                bestPrediction = pre
            }
        })
        return bestPrediction
    }
}