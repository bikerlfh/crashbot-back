import { Prediction } from "../api/models";
import { roundNumber } from "./utils";


export class PredictionCore{
    id: number
    averagePredictionsOfModel: number
    predictionValues: number[] = []
    predictionRounds: number[] = []
    multiplierResults: number[] = []
    categoryPercentages: {[key: number]: number|null} = {
        1: null,
        2: null,
        3: null,
    }
    categoryPercentagesValuesInLive: {[key: number]: number|null} = {
        1: null,
        2: null,
        3: null,
    }

    constructor(
        id: number,
        averagePredictions: number
    ){
        this.id = id
        this.averagePredictionsOfModel = averagePredictions
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
        if(this.categoryPercentages[predictionRound] === null){
            this.categoryPercentages[predictionRound] = categoryPercentage
        }
        if(this.categoryPercentagesValuesInLive[predictionRound] === null){
            this.categoryPercentagesValuesInLive[predictionRound] = categoryPercentage
        }
    }

    addMultiplierResult(multiplier: number){
        this.multiplierResults.push(multiplier)
        this.calculateAverageModelPrediction()
        this.calculateCategoryPercentages()
    }

    calculateCategoryPercentages(){
        let roundMultiplier = 0
        let valueRound = 0
        let value = 0
        for(let i = 1; i <= 2; i++){
            let countI = 0
            let count = 0
            let countValues = 0
            for (let j = 0; j < this.predictionRounds.length; j++){
                valueRound = this.predictionRounds[j]
                value = this.predictionValues[j]
                if(valueRound == i){
                    countI +=1
                    roundMultiplier = roundNumber(this.multiplierResults[j], 0)
                    if(valueRound == roundMultiplier){
                        count++;
                    }
                    if(value <= this.multiplierResults[j]){
                        countValues++;
                    }
                }
            }
            if(count === 0 || countI === 0){
                continue;
            }
            this.categoryPercentages[i] = roundNumber(count / countI, 2);
            this.categoryPercentagesValuesInLive[i] = roundNumber(countValues / countI, 2);
        }
    }

    calculateAverageModelPrediction(){
        let correcValuesCount = 0;
        let roundMultiplier = 0
        for (let i = 0; i < this.multiplierResults.length; i++) {
            roundMultiplier = roundNumber(this.multiplierResults[i], 0)
            if (this.predictionValues[i] == roundMultiplier) {
                correcValuesCount++;
            }
        }
        this.averagePredictionsOfModel = roundNumber(correcValuesCount / this.multiplierResults.length, 2);
    }

    getPreditionValue(): number{
        return this.predictionValues.slice(-1)[0]
    }

    getPredictionRoundValue(): number{
        return this.predictionRounds.slice(-1)[0]
    }

    getCategoryPercentage(): number{
        return this.categoryPercentages[this.getPredictionRoundValue()] || 0
    }
    geCategoryPercentageValueInLive(): number{
        return this.categoryPercentagesValuesInLive[this.getPredictionRoundValue()] || 0
    }
}

export class PredictionModel{
    private static instance: PredictionModel;
    predictions: PredictionCore[] = []
    private MAX_RESULTS_TO_EVALUATE = 15

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
            if(!prediction_){
                prediction_ = new PredictionCore(
                    prediction.id,
                    prediction.averagePredictions
                )
            }   
            prediction_.addPrediction(
                prediction.prediction,
                prediction.predictionRound,
                prediction.averagePredictions,
                prediction.categoryPercentage
            )
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

    evaluateModels(minBotAveragePredictionModel: number){
        this.predictions = this.predictions.filter(p => 
            p.averagePredictionsOfModel > minBotAveragePredictionModel || 
            p.multiplierResults.length < this.MAX_RESULTS_TO_EVALUATE
        );
    }

    getBestPrediction(): PredictionCore|null{
        if(this.predictions.length == 0){
            return null
        }
        let bestPrediction = this.predictions[0]
        this.predictions.forEach(pre => {
            if(pre.averagePredictionsOfModel > bestPrediction.averagePredictionsOfModel){
                bestPrediction = pre
            }
        })
        return bestPrediction
    }
}