const enum GUIEvent {
    LOG = 'log',
    UPDATE_BALANCE = 'update_balance',
    ERROR = 'error',
    EXCEPTION = 'exception',
}


// TODO: add BET_PLACED, BET_WON, BET_LOST
export const enum LogCode {
    INFO = 'info',
    ERROR = 'error',
    WARNING = 'warning',
    SUCCESS = 'success',
    INTERNAL = 'internal',
}

export const sendEventToGUI = {
    log: (data: any, code?: LogCode) => {
        /*
        * Send a log to the GUI
        * @param data: any (can be string or object)
        * @param code: string
        * @return void
        * @example sendLogToGUI('Hello world', 'info')
        * @example sendLogToGUI('Hello world')
        */
        code = code || LogCode.INFO;
        data = typeof data === 'string' ? {message: data} : data;
        data = Object.assign({code:code}, data)
        console.log(data);
        (global as any).emitToGUI(GUIEvent.LOG, data);
    },
    balance: (balance: number) => { 
        (global as any).emitToGUI(GUIEvent.UPDATE_BALANCE, {
            balance: balance
        });
    },
    error: (error: any) => {
        (global as any).emitToGUI(GUIEvent.ERROR, {
            error: error
        });
    },
    exception: (exception: any) => {
        console.log(exception);
        (global as any).emitToGUI(GUIEvent.EXCEPTION, {
            exception: exception.toString()
        });
    }
}
