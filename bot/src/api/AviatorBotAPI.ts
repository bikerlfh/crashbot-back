/**
 * Copyright (c) 2023, lhenriquez.
 * All rights reserved.
 *
 * contains all the endpoints of the api. 
 * The parameters of the url are passed in the form of a dictionary
 * the url that needs url parameters but not GET must be put
 * in the following form: <nombreParametro>, example in the url productDetail
 * @version 1.3
 */
import {Dictionary} from '../types/interfaces';
import {Prediction, BetData, Bot} from './models';

import { ApiService } from './APIAxios';
import { HTTPStatus } from './constants';
const apiService = new ApiService();

const URLS = {
    login: '/api/token/',
    tokenRefresh: '/api/token/refresh/',
    tokenVerify: '/api/token/verify/',
    homeBet: 'home-bet/',
    homeBetDetail: 'home-bet/?P<nombreParametro>',
    addMultipliers: 'home-bet/multiplier/',
    getPrediction: 'predictions/predict/',
    getBots: 'predictions/bots/?bot_type=<bot_type>',
    updateBalance: 'customers/balance/',
    createBet: 'bets/',
    getBet: 'bets/?bet_id=<bet_id>',
};

/**
 * make the url with the parameters
 * @param url: endpoint
 * @param params: params of the url
 * @returns url with the parameters
 */
const makeURL = (url: string, params: Dictionary<any>) =>{
    if(params !== null) {
        // evaluating the parameters that are not GET
        const paramsRequiredList = url.match(/\<\w*\>/g);
        if(paramsRequiredList !== null && paramsRequiredList.length > 0){
            for(let key of paramsRequiredList){
                let keyFormat = key.replace(/\</g,"").replace(/\>/g,"");
                if(params.hasOwnProperty(keyFormat)) {
                    if(params[keyFormat] !== null)
                        url = url.replace("<" + keyFormat + ">", params[keyFormat]);
                    // deleting the attribute of the parameters so that 
                    // they are not added as GET parameters
                    delete params[keyFormat];
                }
            }
        }
        for (let key of Object.keys(params)) {
            const value = params[key]
            if(value !== null && value !== undefined)
                url += (url.indexOf('?') === -1 ? "?" : "&") + key + "=" + params[key];
        }
    }
    return url;
};

export class AviatorBotAPI {
    static requestLogin = async (username: string, password: string) => {
        return await apiService.post(URLS.login, {
            username: username,
            password: password
        })
    }
    static requestTokenRefresh = async (token: string) => {
        return await apiService.post(URLS.tokenRefresh, {
            refresh: token
        });
    }
    static requestTokenVerify = async (token: string) => {
        return await apiService.post(URLS.tokenVerify, {
            token: token
        });
    }
    static requestHomeBet = async () => {
        return await apiService.get(URLS.homeBet);
    }
    static requestHomeBetDetail = async (homeBetId: number) => {
        return await apiService.get(makeURL(URLS.homeBetDetail, {
            home_bet_id: homeBetId
        }));
    }
    static requestSaveMultipliers = (homeBetId: number, multipliers: number[]) => {
        return apiService.post(URLS.addMultipliers, {
            home_bet_id: homeBetId,
            multipliers: multipliers
        }).then((response: any) => {
            if(response.status === HTTPStatus.UNAUTHORIZED){
                console.log(`Unauthorized ${response.request.path}`);
            }
            return response;
        });
    }
    static requestPrediction = async (
        homeBetId: number,
        multipliers?: number[], 
        modelId?: number
    ): Promise<Prediction[]> => {
        return await apiService.post(URLS.getPrediction, {
            home_bet_id: homeBetId,
            multipliers: multipliers || null,
            model_home_bet_id: modelId || null
        }).then((response: any) => { 
            if(response.status === HTTPStatus.UNAUTHORIZED){
                return []
            }
            return response.data.predictions.map((prediction: any) => new Prediction(prediction));
        });
    }
    static requestGetBots = async (botType: string): Promise<Bot[]>  => {
        return await apiService.get(makeURL(URLS.getBots, {
            bot_type: botType
        })).then((response: any) => {
            if(response.status === HTTPStatus.UNAUTHORIZED){
                return []
            }
            return response.data.bots.map(
                (bot: any) => new Bot(bot)
            )
        });
    }
    static requestUpdateBalance = async (customerId: number, homeBetId: number, amount: number) => {
        return await apiService.patch(URLS.updateBalance, {
            customer_id: customerId,
            home_bet_id: homeBetId,
            amount: amount
        });
    }
    static requestCreateBet = async (
        homeBetId: number,
        balance: number,
        bets: BetData[]
    ) => {
        return await apiService.post(URLS.createBet, {
            home_bet_id: homeBetId,
            balance_amount: balance,
            bets: bets.map((bet) => bet.toDict())
        });
    }
    static requestGetBet = async (betId:number) => {
        return await apiService.get(makeURL(URLS.createBet, {bet_id: betId}));
    }
}