"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.APIRest = void 0;
const common_1 = require("../types/common");
const constants_1 = require("./constants");
/**
* format parameters to stringify
* @param params
* @returns {null|string} (JSON.stringify(params))
*/
const formatParameters = (params) => {
    if (params !== null) {
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
exports.APIRest = {
    /**
     * send request to server
     * @param url: url
     * @param method: APIMethod (GET, POST, PUT, PATCH, DELETE)
     * @param body: parametros enviados al server
     * @returns {Promise.<TResult>}
     * @constructor
     */
    HttpRequest(url, method, body) {
        let token = null;
        let config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: body ? JSON.stringify(body) : null,
        };
        if (token !== null)
            config['headers']['Authorization'] = 'token ' + token;
        url = constants_1.APIUrl + url;
        return fetch(url, config)
            .then(response => {
            return response.json().then(res => ({
                ok: response.ok,
                status: response.status,
                data: res
            }));
        })
            .then((response) => {
            if (!response.ok)
                throw response;
            return response.data;
        });
    },
    get(url) {
        return this.HttpRequest(url, common_1.APIMethod.GET);
    },
    post(url, params) {
        return this.HttpRequest(url, common_1.APIMethod.POST, params);
    },
    put(url, params) {
        return this.HttpRequest(url, common_1.APIMethod.PUT, params);
    },
    patch(url, params) {
        return this.HttpRequest(url, common_1.APIMethod.PATCH, params);
    },
};
//# sourceMappingURL=ApiRest.js.map