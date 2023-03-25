import {Multiplier, Bet} from "./core"
import {AviatorBotAPI} from "../api/AviatorBotAPI"
import { HomeBet } from "../constants"
import { PredictionModel, PredictionCore } from "./PredictionCore"
import { WebSocketClient } from "../ws/client"
import { AviatorPage } from "../aviator/Aviator"
import { Control } from '../aviator/BetControl';
import { BetData } from "../api/models"
import { GenerateRandomMultiplier, sleepNow, roundNumber } from "./utils"


export class Game {
    private aviatorPage: AviatorPage
    private _minBet: number = 0
    private _maxBet: number = 0
    private minimumBet: number = 0
    private maximumBet: number = 0
    private maximumWinForOneBet: number = 0
    private _prediction_model: PredictionModel
    private _ws_client?: WebSocketClient
    private initialized: boolean = false
    // automatic betting
    private autoPlay: boolean = false
    homeBet: HomeBet
    initialBalance: number = 0
    balance: number = 0
    multipliers: Multiplier[] = []
    bets: Bet[] = []
    
    
    constructor(homeBet: HomeBet, autoPlay: boolean){
        this.homeBet = homeBet
        this.autoPlay = autoPlay
        this.aviatorPage = homeBet.aviatorPage       
        this.minimumBet = homeBet.minBet
        this.maximumBet = homeBet.maxBet
        this.maximumWinForOneBet = this.maximumBet * 100
        this._prediction_model = PredictionModel.getInstance()
        // globals.homeBetId = this.homeBet.id
    }

    private wsOnMessage(event: any){
        /*
        * Handle the websocket messages to create bets
        */
        try{
            const data = JSON.parse(event.data)
            const homeBetId = data.hasOwnProperty("home_bet_id")? data.home_bet_id: null
            const minMultiplier = data.hasOwnProperty("min_multiplier")? data.min_multiplier: null
            const maxMultiplier = data.hasOwnProperty("max_multiplier")? data.max_multiplier: null
            const chatId = data.hasOwnProperty("chat_id")? data.chat_id: null
            const others = data.hasOwnProperty("others")? data.others: null
            if(!homeBetId || !minMultiplier || !maxMultiplier){
                console.error("socketOnMessage: data incomplete")
                return
            }
            if(homeBetId != this.homeBet.id){
                // the home bet of the bet is not the same as the current home bet
                return
            }
            // TODO: fix this. Amount should be calculated from the multiplier
            //const amount = this.calculateAmountBet(minMultiplier)
            const amount = this.validateBetAmount(roundNumber(this.balance * 0.1))
            const amount2 = this.validateBetAmount(roundNumber(amount / 3))
            this.bets.push(new Bet(amount, minMultiplier))
            this.bets.push(new Bet(amount2, maxMultiplier))
            this.sendBetsToAviator(this.bets).then(() => {}).catch(error => {
                this.bets = []
            })
        }catch(error){
            console.error("socketOnMessage:", error)
        }
    }

    async initialize(){
        /* 
        * Init the game
        * - init the websocket
        * - Open the browser
        */
        console.log("connecting to websocket.....")
        this._ws_client = await WebSocketClient.getInstance()
        console.log("opening home bet.....")
        await this.aviatorPage.open()
        console.log("reading the player's balance.....")
        this.initialBalance = await this.readBalanceToAviator()
        this.balance = this.initialBalance
        const multipliers = this.aviatorPage.multipliers
        this.multipliers = multipliers.map(item => new Multiplier(item))
        console.log("saving intial multipliers.....")
        this.requestSaveMultipliers(multipliers)
        this._ws_client.setOnMessage(this.wsOnMessage.bind(this))
        this.calculateMinMaxBet()
        this.initialized = true
        console.clear()
        console.log("Game initialized")
    }

    async readBalanceToAviator(){
        /*
        * Read the balance from the Aviator
        */
        return await this.aviatorPage.readBalance() || 0
    }

    private requestSaveMultipliers(multipliers: number[]){
        /*
        * Save the multipliers in the database
        */
        AviatorBotAPI.requestSaveMultipliers(this.homeBet.id, multipliers).catch(
            error => {
                console.error("error in requestSaveMultipliers:", error)
            }
        )
    }

    private requestSaveBets(bets: Bet[]){
        /*
        * Save the bets in the database
        */
        if(bets.length == 0){
            return
        }
        const betsToSave = bets.map(bet => { 
            return new BetData(
                bet.externalId,
                bet.prediction,
                bet.multiplier,
                bet.amount,
                bet.multiplierResult
            )
        })
        AviatorBotAPI.requestCreateBet(
            1,
            this.homeBet.id,
            betsToSave
        ).catch(error => {console.error("error in requestSaveBets:", error)})
    }

    private async requestGetPrediction(): Promise<PredictionCore|null>{
        /*
        * Get the prediction from the database
        */
        const predictions = await AviatorBotAPI.requestPrediction(this.homeBet.id).catch(
            error => { return [] }
        )
        this._prediction_model.addPredictions(predictions)
        return this._prediction_model.getBestPrediction()
    }

    private async waitNextGame(){
        /**
         * Wait for the next game to start
         */
        await this.aviatorPage.waitNextGame()
        this.balance = await this.readBalanceToAviator()
        this.addMultiplier(this.aviatorPage.multipliers.slice(-1)[0])
        this.bets = []
        console.clear()
    }

    private async sendBetsToAviator(bets : Bet[]){
        /**
         * Send the bets to the Aviator
         */
        if(bets.length == 0){
            return
        }
        for (let index = 0; index < bets.length; index++) {
            const bet = bets[index];
            const control = index == 0? Control.Control1: Control.Control2
            console.log("sending bet to aviator %d * %d control: %s", bet.amount, bet.multiplier, control)
            await this.aviatorPage.bet(bet.amount, bet.multiplier, control)
            await sleepNow(2000)
        }
    }

    async play(){
        /*
        * Play the game
        */
        if (!this.initialized){
            console.error("The game is not initialized")
            return
        }
        while(this.initialized){
            await this.waitNextGame()
            if(this.autoPlay){
                await this.getNextBet()
                await this.sendBetsToAviator(this.bets)
            }
        }
    }

    private validateBetAmount(amount: number){
        if(amount < this.minimumBet){
            amount = this.minimumBet
        }else if(amount > this.maximumBet){
            amount = this.maximumBet
        }
        if(amount > this.balance){
            amount = this.balance
        }
        return amount
    }

    private evaluateBets(multiplier: number){
        if(this.bets.length == 0){
            return
        }
        this.bets.forEach(bet=>{
            const profit = bet.evaluate(multiplier)
            this.balance += profit
        })
    }

    private addMultiplier(multiplier: number){
        this._prediction_model.addMultiplierResult(multiplier)
        this.evaluateBets(multiplier)
        this.multipliers.push(new Multiplier(multiplier))
        this.requestSaveMultipliers([multiplier])
        this.requestSaveBets(this.bets)
    }


    calculateMinMaxBet(){
        const numMinBets = this.balance / this.minimumBet
        if(numMinBets <= 50){
            // if the balance is less than 50 minimum bets, the minimum bet is the minimum bet
            // and the maximum bet is 3 times the minimum bet
            this._minBet = this.minimumBet
            this._maxBet = parseFloat((this.minimumBet * (numMinBets * 3)).toFixed(0))
            return
        }
        // if the balance is more than 50 minimum bets, the minimum bet is 0.3% of the balance
        this._minBet = parseFloat((this.minimumBet * (numMinBets * 0.003)).toFixed(0))
        // and the maximum bet is 0.8% of the balance
        this._maxBet = parseFloat((this.minimumBet * (numMinBets * 0.008)).toFixed(0))
    }

    calculateAmountBet(multiplier: number, usedAmount?: number): number{
        usedAmount = usedAmount || 0
        let balance = this.balance - usedAmount
        let profit = balance - this.initialBalance
        let amount = this._minBet
        console.log("balance: ", balance, "; profit: ", profit, "; amount: ", amount)
        if(profit < 0){
            amount = (Math.abs(profit) / (multiplier -1)) + this._minBet
        }
        else{
            amount *= 2
        }
        amount = amount > this.minimumBet? amount: this.minimumBet;
        if(amount > balance){
            amount = balance
        }
        if(amount > this.maximumBet){
            amount = this.maximumBet
        }
        if(amount < 0){
            amount = this._minBet
        }
        amount = parseFloat(amount.toFixed(0))
        return amount
    }

    async getNextBet(): Promise<Bet[]>{
        this.bets = []
        const prediction = await this.requestGetPrediction()
        if(prediction == null){
            return []
        }
        const profit = this.balance - this.initialBalance
        const categoryPrecentage = prediction.getCategoryPercentage()
        const predictionRound = prediction.getPredictionRoundValue()
        let predictionValue = prediction.getPreditionValue()
        const averagePredictionValuesInLive = prediction.averagePredictionValuesInLive
        const averagePredictionInLive = prediction.averagePredictionInLive
        console.log(
            "predictionRound: ", predictionRound,
            "predictionValue: ", predictionValue,
            "ValuesInLive: ", averagePredictionValuesInLive,
            "InLive: ", averagePredictionInLive,
            "categoryPrecentage: ", categoryPrecentage,
        )
        if(predictionValue < 0){
            predictionValue = 1.1
        }
        if(predictionRound == 1){
            if(averagePredictionValuesInLive < 70){
                return []
            }
            this.bets.push(new Bet(this.calculateAmountBet(predictionValue), predictionValue))
            return this.bets
        }
        if(predictionRound == 2){
            if(averagePredictionInLive < 70){
                if(profit < 0){
                    return []
                }
                this.bets.push(new Bet(this.calculateAmountBet(predictionValue), predictionValue)) 
                return this.bets
            }
            if(profit < 0){
                this.bets.push(new Bet(this.calculateAmountBet(predictionRound), predictionRound))
            }else{
                const amount = this.calculateAmountBet(1.95)
                this.bets.push(new Bet(amount, 1.95))
                const amount2 = parseFloat((amount / 3).toFixed(2))
                this.bets.push(new Bet(amount2, GenerateRandomMultiplier(2, 3)))
            }
            return this.bets
        }    
        if(averagePredictionInLive < 70){
            if(profit > 0){
                this.bets.push(new Bet(this.calculateAmountBet(predictionRound), predictionRound))
                return this.bets
            }
            return []
        }
        const amount = this.calculateAmountBet(1.95)
        this.bets.push(new Bet(amount, 1.95))
        if(profit > 0){
            const amount2 = parseFloat((amount / 3).toFixed(2))
            this.bets.push(new Bet(amount2, 1.95))
        }
        return this.bets
    }
}
