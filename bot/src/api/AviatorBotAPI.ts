/**
 * Copyright (c) 2018, Neubs SAS.
 * All rights reserved.
 *
 * Contiene todos los enpoints de la api.
 * Las cadenas que necesiten parametros de url mas no GET se deben poner
 * de la siguiente forma: (?P<nombreParametro>), ejemplo en la url productoDetalle
 * @version 1.3
 */
import {Dictionary} from '../types/interfaces';
import {APIRest} from './APIRest';
import {Prediction, BetData, PlayerStrategy} from './models';


const URLS = {
    /** Authentication **/
    homeBet: 'home-bet/',
    homeBetDetail: 'home-bet/?P<nombreParametro>',
    addMultipliers: 'home-bet/multiplier/',
    getPrediction: 'predictions/predict/',
    getStrategies: 'predictions/strategy/',
    updateBalance: 'customers/balance/',
    createBet: 'bets/',
    getBet: 'bets/?P<bet_id>',
    // gameDetail: 'games/<gameId>/',
};

/**
 * Construye la url de las peticiones a la API
 * @param url: url del objeto URLS
 * @param params: parámetros a pasar
 * @returns url con los parámetros
 */
const makeURL = (url: string, params: Dictionary<any>) =>{
    if(params !== null) {
        // se evaluan los parametros no GET que van en la url
        const paramsRequiredList = url.match(/\<\w*\>/g);
        if(paramsRequiredList !== null && paramsRequiredList.length > 0){
            for(let key of paramsRequiredList){
                let keyFormat = key.replace(/\</g,"").replace(/\>/g,"");
                if(params.hasOwnProperty(keyFormat)) {
                    if(params[keyFormat] !== null)
                        url = url.replace("<" + keyFormat + ">", params[keyFormat]);
                    // se elimina el atributo de los parámetors para que
                    // no se agregen como parametros GET
                    delete params[keyFormat];
                }
            }
        }
        // Se agregan los parametros GET
        for (let key of Object.keys(params)) {
            const value = params[key]
            if(value !== null && value !== undefined)
                url += (url.indexOf('?') === -1 ? "?" : "&") + key + "=" + params[key];
        }
    }
    return url;
};

export class AviatorBotAPI {
    static requestHomeBet = async () => {
        return await APIRest.get(URLS.homeBet);
    }
    static requestHomeBetDetail = async (homeBetId: number) => {
        return await APIRest.get(makeURL(URLS.homeBetDetail, {
            home_bet_id: homeBetId
        }));
    }
    static requestSaveMultipliers = (homeBetId: number, multipliers: number[]) => {
        return APIRest.post(URLS.addMultipliers, {
            home_bet_id: homeBetId,
            multipliers: multipliers
        });
    }
    static requestPrediction = async (
        homeBetId: number,
        multipliers?: number[], 
        modelId?: number
    ): Promise<Prediction[]> => {
        return await APIRest.post(URLS.getPrediction, {
            home_bet_id: homeBetId,
            multipliers: multipliers || null,
            model_home_bet_id: modelId || null
        }).then((response: any) => { 
            return response.predictions.map((prediction: any) => new Prediction(prediction));
        });
    }
    static requestGetStrategies = async (): Promise<PlayerStrategy[]>  => {
        return await APIRest.get(URLS.getStrategies).then(
            (response: any) => response.strategies.map(
                (strategy: any) => new PlayerStrategy(strategy)
            )
        );
    }
    static requestUpdateBalance = async (customerId: number, homeBetId: number, amount: number) => {
        return await APIRest.patch(URLS.updateBalance, {
            customer_id: customerId,
            home_bet_id: homeBetId,
            amount: amount
        });
    }
    static requestCreateBet = async (
        customerId: number, 
        homeBetId: number,
        bets: BetData[]
    ) => {
        return await APIRest.post(URLS.createBet, {
            customer_id: customerId,
            home_bet_id: homeBetId,
            bets: bets.map((bet) => bet.toDict())
        });
    }
    static requestGetBet = async (betId:number) => {
        return await APIRest.get(makeURL(URLS.createBet, {bet_id: betId}));
    }
}