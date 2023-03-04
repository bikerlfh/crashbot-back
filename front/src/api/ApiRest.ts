/**
 * Copyright (c) 2023, luisferhenriquez.
 * All rights reserved.
 *
 * Maneja las peticiones a la api. Solo se debe acceder mediante
 * métodos de la clase APIRequest
 *
 * @example
 * import APIRest from './lib/APIRest';
 * APIRest.get(URL)
 *  .then((res)=>{
 *      ...
 *  })
 *  .catch((err)=>{
 *      ...
 *  });
 * @version 1.0
 */
import {Dictionary} from '../types/interfaces';
import {APIMethod} from '../types/common';
import {APIKey, APIUrl, HTTPStatus} from './constants';

/**
* format parameters to stringify
* @param params
* @returns {null|string} (JSON.stringify(params))
*/
const formatParameters = (params: Dictionary<any>) => {
   if(params !== null) {
       for (let key of Object.keys(params)) {
           // si el atributo es una instancia de Date
           if (params[key] instanceof Date) {
               // ojo se usa la libreria momentjs (fromat es ProtoType de Date)
               params[key] = params[key].format("YYYY-MM-DD H:mm:ss");
           }
       }
       return JSON.stringify(params);
   }
   return null;
};

export let APIRest = {
   /**
    * send request to server
    * @param url: url
    * @param method: APIMethod (GET, POST, PUT, PATCH, DELETE)
    * @param body: parametros enviados al server
    * @returns {Promise.<TResult>}
    * @constructor
    */
   HttpRequest(url: string, method: APIMethod, body?: Dictionary<any>): Promise<any> {
       let token = null;
       let config: Dictionary<any> = {
           method: method,
           headers: {
               'Content-Type': 'application/json',
           },
           body: body? JSON.stringify(body) : null,
       };
       
       if(token !== null)
           config['headers']['Authorization'] = 'token ' + token;
       url =  APIUrl + url;
       console.log(config)
       return fetch(url, config)
           .then(response => {
               return response.json().then(res =>({ 
                       ok: response.ok, 
                       status: response.status, 
                       data: res
                   }
               ));
           })
           .then((response: any) => {
               if(!response.ok)
                   throw response
               return response.data;
           }).catch((err) => { 
                console.log(
                    "fetch :: url :: ", 
                    url, 
                    " error: ", 
                    JSON.stringify(err)
                );
                throw err;
           });
   },
   get(url: string) {
       return this.HttpRequest(url, APIMethod.GET);
   },
   post(url: string, params: Dictionary<any>){
       return this.HttpRequest(url, APIMethod.POST, params);
   },
   put(url: string, params: Dictionary<any>){
       return this.HttpRequest(url, APIMethod.PUT, params);
   },
   patch(url: string, params: Dictionary<any>){
       return this.HttpRequest(url, APIMethod.PATCH, params);
   },
};
