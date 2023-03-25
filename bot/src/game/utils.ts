 export const GenerateRandomMultiplier = (min: number, max: number): number  => {
    const precision = 100;
    const randomNum = Math.floor(
        Math.random() * (max * precision - min * precision) + 1 * precision
    ) / (min * precision);
    return randomNum
}

export const sleepNow = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay))


export const roundNumber = (num: number, decimalPlaces?: number, aprox?: boolean) => {
    decimalPlaces = decimalPlaces || 0
    aprox = aprox || false
    if(aprox){
        return Math.round(num * Math.pow(10, decimalPlaces)) / Math.pow(10, decimalPlaces)
    }
    return parseFloat(num.toFixed(decimalPlaces))
}
