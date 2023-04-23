import { Prediction } from "../api/models";
import { roundNumber } from "./utils";
import { sendEventToGUI } from "../ws/gui_events";


export class PredictionCore{
    id: number
    averagePredictionsOfModel: number
    predictionValues: number[] = []
    predictionRounds: number[] = []
    probabilityValues: number[] = []
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
        probability: number,
        averagePredictions: number,
        categoryPercentage: number = 0
    ){
        this.predictionValues.push(prediction)
        this.predictionRounds.push(predictionRound)
        this.probabilityValues.push(probability)
        this.averagePredictionsOfModel = averagePredictions
        if(this.categoryPercentages[predictionRound] === null){
            this.categoryPercentages[predictionRound] = categoryPercentage
        }
        if(this.categoryPercentagesValuesInLive[predictionRound] === null){
            this.categoryPercentagesValuesInLive[predictionRound] = categoryPercentage
        }
        sendEventToGUI.log.debug("---------------------- PredictionCore: addPrediction ----------------------")
        sendEventToGUI.log.debug(`Model ID: ${this.id}`)
        sendEventToGUI.log.debug(`Added prediction: ${prediction}(${predictionRound}) - probability: ${probability}`)
    }

    addMultiplierResult(multiplier: number){
        this.multiplierResults.push(multiplier)
        this.calculateAverageModelPrediction()
        this.calculateCategoryPercentages()
    }

    calculateCategoryPercentages(){
        //sendEventToGUI.log.debug("------------- PredictionCore: calculateCategoryPercentages -------------")
        //sendEventToGUI.log.debug(`Model ID: ${this.id}`)
        //sendEventToGUI.log.debug(`Prediction Rounds: ${this.predictionRounds}`)
        //sendEventToGUI.log.debug(`Prediction Values: ${this.predictionValues}`)
        //sendEventToGUI.log.debug(`Multiplier Results: ${this.multiplierResults}`)
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
                    roundMultiplier = roundMultiplier >= 2 ? 2 : roundMultiplier
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
            //sendEventToGUI.log.debug(`Category ${i}: ${this.categoryPercentages[i]}`)
            //sendEventToGUI.log.debug(`Category ${i} Values: ${this.categoryPercentagesValuesInLive[i]}`)
        }
    }

    calculateAverageModelPrediction(){
        //sendEventToGUI.log.debug("------------- PredictionCore: calculateAverageModelPrediction -------------")
        let correcValuesCount = 0;
        let roundMultiplier = 0
        for (let i = 0; i < this.multiplierResults.length; i++) {
            roundMultiplier = roundNumber(this.multiplierResults[i], 0)
            roundMultiplier = roundMultiplier >= 2 ? 2 : roundMultiplier
            if (this.predictionRounds[i] == roundMultiplier) {
                correcValuesCount++;
            }
        }
        this.averagePredictionsOfModel = roundNumber(correcValuesCount / this.multiplierResults.length, 2);
        //sendEventToGUI.log.debug(`Model ID: ${this.id}`)
        //sendEventToGUI.log.debug(`Prediction Rounds: ${this.predictionRounds}`)
        //sendEventToGUI.log.debug(`Multiplier Results: ${this.multiplierResults}`)
        //sendEventToGUI.log.debug(`Correct Values: ${correcValuesCount}`)
        //sendEventToGUI.log.debug(`Count Multiplier Results: ${this.multiplierResults.length}`)
        //sendEventToGUI.log.debug(`Average Predictions: ${this.averagePredictionsOfModel})`)
    }

    getPreditionValue(): number{
        return this.predictionValues.slice(-1)[0]
    }

    getPredictionRoundValue(): number{
        return this.predictionRounds.slice(-1)[0]
    }

    getProbabilityValue(): number{
        return this.probabilityValues.slice(-1)[0]
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
    private MAX_RESULTS_TO_EVALUATE = 18

    private constructor() { }

    public static getInstance(): PredictionModel {
        if (!PredictionModel.instance) {
            PredictionModel.instance = new PredictionModel();
        }
        return PredictionModel.instance;
    }

    addPredictions(predictions: Prediction[]){
        //sendEventToGUI.log.debug("----------------- PredictionModel: addPredictions ------------------")
        //sendEventToGUI.log.debug(`Count Predictions: ${this.predictions.length}`)
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
                //sendEventToGUI.log.debug(`New PredictionCore: ${prediction.id}`)
            }   
            prediction_.addPrediction(
                prediction.prediction,
                prediction.predictionRound,
                prediction.probability,
                prediction.averagePredictions,
                prediction.categoryPercentage
            )
            new_predictions.push(prediction_)
        })
        this.predictions = new_predictions
        //sendEventToGUI.log.debug(`Next Count Predictions: ${this.predictions.length}`)
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
        //sendEventToGUI.log.debug("----------------- PredictionModel: evaluateModels ------------------")
        //sendEventToGUI.log.debug(`Count Prediction: ${this.predictions.length}`)
        this.predictions = this.predictions.filter(p => 
            p.averagePredictionsOfModel > minBotAveragePredictionModel || 
            p.multiplierResults.length < this.MAX_RESULTS_TO_EVALUATE
        );
        //sendEventToGUI.log.debug(`Next Count Prediction: ${this.predictions.length}`)
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
        //sendEventToGUI.log.debug("----------------- PredictionModel: getBestPrediction ------------------")
        //sendEventToGUI.log.debug(`Model ID: ${bestPrediction.id}`)
        return bestPrediction
    }
}