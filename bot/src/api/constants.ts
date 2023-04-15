/**
 * APIUrl
 * @type {string}
 */
export const APIUrl = "http://localhost:8000/";
// export const APIUrl: string = "http://201.244.226.121:8081/";

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