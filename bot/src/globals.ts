export const createGlobals = (io: any|null) => {
    /*
    * Create the global variables
    * use this function to initialize the global variables
    */
    (global as any).autoPlay = false;
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
