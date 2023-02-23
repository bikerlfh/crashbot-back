/**
 * Url de la api
 * @type {string}
 */
export const APIUrl: string = "http://201.244.226.121:8081/";
//export const APIUrl = "http://127.0.0.1:8000/";
export const APIKey: string = "edd19a46ed105cf8fb22056328072bec";

export enum HTTPStatus {
    OK = 200,
    CREATED = 201,
    BAD_REQUEST = 400,
    UNAUTHORIZED = 401,
    FORBIDDEN = 403,
    NOT_FOUND = 404,
    METHOD_NOT_ALLOWED = 405,
    CONFLICT = 409,
    INTERNAL_ERROR = 500,
    NOT_IMPLEMENTED = 501
}