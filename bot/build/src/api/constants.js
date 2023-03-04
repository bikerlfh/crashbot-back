"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HTTPStatus = exports.APIKey = exports.APIUrl = void 0;
/**
 * Url de la api
 * @type {string}
 */
exports.APIUrl = "http://201.244.226.121:8081/";
//export const APIUrl = "http://127.0.0.1:8000/";
exports.APIKey = "edd19a46ed105cf8fb22056328072bec";
var HTTPStatus;
(function (HTTPStatus) {
    HTTPStatus[HTTPStatus["OK"] = 200] = "OK";
    HTTPStatus[HTTPStatus["CREATED"] = 201] = "CREATED";
    HTTPStatus[HTTPStatus["BAD_REQUEST"] = 400] = "BAD_REQUEST";
    HTTPStatus[HTTPStatus["UNAUTHORIZED"] = 401] = "UNAUTHORIZED";
    HTTPStatus[HTTPStatus["FORBIDDEN"] = 403] = "FORBIDDEN";
    HTTPStatus[HTTPStatus["NOT_FOUND"] = 404] = "NOT_FOUND";
    HTTPStatus[HTTPStatus["METHOD_NOT_ALLOWED"] = 405] = "METHOD_NOT_ALLOWED";
    HTTPStatus[HTTPStatus["CONFLICT"] = 409] = "CONFLICT";
    HTTPStatus[HTTPStatus["INTERNAL_ERROR"] = 500] = "INTERNAL_ERROR";
    HTTPStatus[HTTPStatus["NOT_IMPLEMENTED"] = 501] = "NOT_IMPLEMENTED";
})(HTTPStatus = exports.HTTPStatus || (exports.HTTPStatus = {}));
//# sourceMappingURL=constants.js.map