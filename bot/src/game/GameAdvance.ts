import {Multiplier, Bet} from "./core"
import {AviatorBotAPI} from "../api/AviatorBotAPI"
import { HomeBet } from "../constants"
import { PredictionModel, PredictionCore } from "./PredictionCore"
import { WebSocketClient } from "../ws/client"
import { AviatorPage } from "../aviator/Aviator"
import { Control } from '../aviator/BetControl';
import { BetData } from "../api/models"
import { sleepNow, roundNumber } from "./utils"
import { BotType } from "./core"
import { Bot, BotStatic } from "./bots/bots"


export class Game {
    private MAX_MULTIPLIERS_TO_SAVE: number = 10
    private aviatorPage: AviatorPage
    private minimumBet: number = 0
    private maximumBet: number = 0
    private maximumWinForOneBet: number = 0
    private _prediction_model: PredictionModel
    private _ws_client?: WebSocketClient
    private initialized: boolean = false
    // automatic betting
    private autoPlay: boolean = false
    private bot: Bot|BotStatic
    homeBet: HomeBet
    initialBalance: number = 0
    balance: number = 0
    multipliers: Multiplier[] = []
    multipliersToSave: number[] = []
    bets: Bet[] = []
    
    
    constructor(homeBet: HomeBet, autoPlay: boolean, botType: BotType, useBotStatic?: boolean){
        // TODO: add correct customerId
        this.homeBet = homeBet
        this.autoPlay = autoPlay
        this.aviatorPage = homeBet.aviatorPage       
        this.minimumBet = homeBet.minBet
        this.maximumBet = homeBet.maxBet
        if(!useBotStatic){
            this.bot = new Bot(botType, this.minimumBet, this.maximumBet)
        }
        else{
            this.bot = new BotStatic(botType, this.minimumBet, this.maximumBet)
        }
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
        // NOTE: activate when the websocket is ready
        //this._ws_client = await WebSocketClient.getInstance()
        //this._ws_client.setOnMessage(this.wsOnMessage.bind(this))
        console.log("opening home bet.....")
        await this.aviatorPage.open()
        console.log("reading the player's balance.....")
        this.initialBalance = await this.readBalanceToAviator()
        this.balance = this.initialBalance
        console.log("loading the player.....")
        this.multipliersToSave = this.aviatorPage.multipliers
        this.multipliers = this.multipliersToSave.map(item => new Multiplier(item))
        await this.requestSaveMultipliers()
        await this.bot.initialize(this.initialBalance)
        this.initialized = true
        //console.clear()
        console.log("Game initialized")
    }

    async readBalanceToAviator(){
        /*
        * Read the balance from the Aviator
        */
        return await this.aviatorPage.readBalance() || 0
    }

    private async requestSaveMultipliers(){
        /*
        * Save the multipliers in the database
        */
        if(this.multipliersToSave.length < this.MAX_MULTIPLIERS_TO_SAVE){
            return
        }
        console.log("saving multipliers.....")
        console.log("multipliers to save:", this.multipliersToSave);
        await AviatorBotAPI.requestSaveMultipliers(this.homeBet.id, this.multipliersToSave).then(
            (response) => {
                this.multipliersToSave = []
                console.log("multipliers saved:", response.data.multipliers);
            }
        ).catch(
            (error) => {
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
                roundNumber(bet.amount, 2),
                bet.multiplierResult
            )
        })
        console.log("saving bets.....")
        AviatorBotAPI.requestCreateBet(
            this.homeBet.id,
            roundNumber(this.balance, 2),
            betsToSave
        ).then(
            (response) => {
                console.log("bets saved:", response.data);
            }
        ).catch(error => {console.error("error in requestSaveBets:", error)})
    }

    private async requestGetPrediction(): Promise<PredictionCore|null>{
        /*
        * Get the prediction from the database
        */
        const multipliers = this.multipliers.map(item => item.multiplier)
        const predictions = await AviatorBotAPI.requestPrediction(this.homeBet.id, multipliers).catch(
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
        this.bot.updateBalance(this.balance)
        await this.addMultiplier(this.aviatorPage.multipliers.slice(-1)[0])
        this.bets = []
        //console.clear()
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
            await sleepNow(1000)
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
            await this.getNextBet()
            if(this.autoPlay){
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
        this.bot.evaluateBets(multiplier)
    }

    private async addMultiplier(multiplier: number){
        this._prediction_model.addMultiplierResult(multiplier)
        this.evaluateBets(multiplier)
        this.multipliers.push(new Multiplier(multiplier))
        this.multipliersToSave.push(multiplier)
        this.requestSaveBets(this.bets)
        this.requestSaveMultipliers()
        // remove the first multiplier
        this.multipliers = this.multipliers.slice(1)
    }

    async getNextBet(): Promise<Bet[]>{
        this._prediction_model.evaluateModels(
            this.bot.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET
        )
        const prediction = await this.requestGetPrediction()
        if(prediction == null){
            return []
        }
        this.bets = this.bot.getNextBet(prediction)
        console.log("bets:", this.bets)
        return this.bets
    }
}
