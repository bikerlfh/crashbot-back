export const generateRandomMultiplier = (min: number, max: number): number  =>{
    const randomNum = Math.random() * (max - min) + min;
    const value = Number(randomNum.toFixed(2));
    return value;
  }

export const sleepNow = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay))


export const roundNumber = (num: number, decimalPlaces?: number, aprox?: boolean) => {
    /*
    * @param num is the number to round
    * @param decimalPlaces is the number of decimal places to round to
    * @param aprox is a boolean to round the number to the nearest integer
    * example: roundNumber(1.2345, 2, true)
    * example: roundNumber(1.2345, 2, false)
    * example: roundNumber(1.2345, 2)
    * example: roundNumber(1.2345)
    */
    decimalPlaces = decimalPlaces || 0
    aprox = aprox || false
    if(aprox){
        return Math.round(num * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces)
    }
    return parseFloat(num.toFixed(decimalPlaces))
}

export const formatNumberToMultiple = (num: number, multiple: number): number => {
    /*
    * @param num is the number to format
    * @param multiple is the multiple to format the number
    * example: formatNumerToMultiple(1.2345, 100)
    */
    return Math.round(num / multiple) * multiple
}


export const kellyFormula = (b: number, p:number, capital: number): number => {
    /*
    * The Kelly formula is a formula used to determine the optimal fraction of one's capital to bet on a given bet.
    * The formula is: f* = (bp - q) / b
    * @param b is the ratio of net gains to net losses (i.e., net gains per unit bet),
    * @param p is the probability of winning the bet, and
    * @param q is the probability of losing the bet (q = 1 - p).
    * @param capital is the amount of money you have to bet.
    * example: kellyFormula(2, 0.6, 1000)
    */
    const f = (b * p - (1 - p)) / b;
    return roundNumber(capital * f, 2);
}
  
export const adaptiveKellyFormula = (b: number, p: number, R: number, capital: number): number => {
    /*
    * The Adaptive Kelly formula is a formula used to determine the optimal fraction of one's capital to bet on a given bet.
    * The formula is: f* = (bp - q) / b * (1 + R)
    * @param b is the ratio of net gains to net losses (i.e., net gains per unit bet),
    * @param p is the probability of winning the bet, and
    * @param q is the probability of losing the bet (q = 1 - p).
    * @param R is a risk factor that varies with the volatility of the market,
    * @param capital is the amount of money you have to bet.
    * example: kellyFormula(2, 0.6, 0.1, 1000)
    */
    const f = ((b * p - (1 - p)) / b) * (1 + R);
    return roundNumber(capital * f, 2);
}