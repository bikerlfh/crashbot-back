import {sentLogToGUI} from "../globals"


export enum BotType{
    AGGRESSIVE = "aggressive",
    TIGHT = "tight",
    LOOSE = "loose",
}

export class Multiplier{
    multiplier: number
    category: number
    
    constructor(multiplier: number){
        this.multiplier = multiplier
        if(multiplier < 2){
            this.category = 1
        }else{
            this.category = 2
        }
        // TODO add more categories
        /*else if(multiplier < 10){
            this.category = 2
        }
        else{
            this.category = 3
        }*/
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
    externalId: string
    amount: number = 0
    prediction: number
    multiplier: number = 0
    multiplierResult?: number
    profit: number = 0

    constructor(amount: number, multiplier: number, prediction?: number){
        this.externalId = Math.random().toString(36).substring(2)
        this.multiplier = multiplier
        this.prediction = prediction || this.multiplier
        this.amount = amount
    }

    evaluate(multiplierResult: number): number{
        this.multiplierResult = multiplierResult
        if(multiplierResult >= this.multiplier){
            this.profit += this.amount * (this.multiplier - 1)
        }else{
            this.profit -= this.amount
        }
        return parseFloat(this.profit.toFixed(2))
    }
 }
 

 export class PredictionData{
    constructor(
        public predictionRound: number,
        public predictionValue: number,
        public categoryPrecentage: number,
        public categoryPercentageValueInLive: number,
        public averagePredictionsOfModel: number,
        public inCategoryPrecentage: boolean,
        public inCategoryPercentageValueInLive: boolean,
        public inAveragePredictionsOfModel: boolean
    ){}

    printData(){
        sentLogToGUI(`prediction: ${this.predictionValue}(${this.predictionRound})`)
        sentLogToGUI(`categoryPrecentage: ${this.categoryPrecentage}`)
        sentLogToGUI(`categoryPercentageValueInLive: ${this.categoryPercentageValueInLive}`)
        sentLogToGUI(`averagePredictionsOfModel: ${this. averagePredictionsOfModel}`)
        sentLogToGUI(`inCategoryPercentageValueInLive: ${this.inCategoryPercentageValueInLive}`)
        sentLogToGUI(`inCategoryPrecentage: ${this.inCategoryPrecentage}`)
        sentLogToGUI(`inAveragePredictionsOfModel: ${this.inAveragePredictionsOfModel}`)
    }
 }