export const makeWSError = (message: string, code?: string): any => {
    code = code || 'error'
    return {error: {code: code, message: message}}
}