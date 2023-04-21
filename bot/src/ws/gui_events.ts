const enum GUIEvent {
    LOG = 'log',
    UPDATE_BALANCE = 'update_balance',
    ERROR = 'error',
    EXCEPTION = 'exception',
}


// TODO: add BET_PLACED, BET_WON, BET_LOST
export const enum LogCode {
    INFO = 'info',
    SUCCESS = 'success',
    WARNING = 'warning',
    ERROR = 'error',
    DEBUG = 'debug',
}

const sendLogToGUI = (data: any, code?: LogCode) => {
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
}

export const sendEventToGUI = {
    log: {
        info: (data: any) => {
            sendLogToGUI(data, LogCode.INFO);
        },
        error: (data: any) => {
            sendLogToGUI(data, LogCode.ERROR);
        },
        warning: (data: any) => {
            sendLogToGUI(data, LogCode.WARNING);
        },
        success: (data: any) => {
            sendLogToGUI(data, LogCode.SUCCESS);
        },
        debug: (data: any) => {
            sendLogToGUI(data, LogCode.DEBUG);
        },
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
