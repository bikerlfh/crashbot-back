// export const URL_AVIATOR_DEMO: string = "https://www.spribe.co/games/aviator"
// export const URL_AVIATOR_DEMO: string = "https://aviator-demo.spribegaming.com/?currency=USD&operator=demo&jurisdiction=CW&lang=EN&return_url=https:%2F%2Fspribe.co%2Fgames&user=59702&token=s7p0PCPnR5mp2yyQilRG0QdUrV0CiS2l"
// export const URL_BETPLAY: string = "https://betplay.com.co/slots"



export let HomeBet = {
    demo: {
        id: 1,
        url: "https://www.spribe.co/games/aviator"
    },
    betplay: {
        id: 2,
        url:  "https://betplay.com.co/slots",
        username: process.env.BET_PLAY_USERNAME,
        password: process.env.BET_PLAY_PASSWORD
    },
    oneWin: {
        id: 3,
        url: "https://1wslue.top/casino/",
        username: process.env.ONE_WIN_USERNAME,
        password: process.env.ONE_WIN_PASSWORD
    }
}