 export const GenerateRandomMultiplier = (min: number, max: number): number  => {
    const precision = 100;
    const randomNum = Math.floor(
        Math.random() * (max * precision - min * precision) + 1 * precision
    ) / (min * precision);
    return randomNum
}

export const sleepNow = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay))
