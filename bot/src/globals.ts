export const createGlobals = (io: any|null) => {
    /*
    * Create the global variables
    * use this function to initialize the global variables
    */
    (global as any).autoPlay = false;
    // (global as any).homeBetId = false;
    // (global as any).customerId = false;
    (global as any).maxAmountToBet = 300;
    (global as any).game = null;
    (global as any).emitToGUI = (event: string, message: any) =>{
        if(io){
            io.emit(event, message);
            return
        }
        console.log('No io instance');
    };
}

export const enum LogCode {
    INFO = 'info',
    ERROR = 'error',
    WARNING = 'warning',
    SUCCESS = 'success',
} 

export const sentLogToGUI = (data: any, code?: LogCode) => {
    /*
    * Send a log to the GUI
    * @param data: any (can be string or object)
    * @param code: string
    * @return void
    * @example sentLogToGUI('Hello world', 'info')
    * @example sentLogToGUI('Hello world')
    */
    code = code || LogCode.INFO;
    data = typeof data === 'string' ? {message: data} : data;
    data = Object.assign({code:code}, data)
    console.log(data);
    (global as any).emitToGUI('log', data);
}