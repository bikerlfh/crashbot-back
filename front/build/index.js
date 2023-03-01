"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const constants_1 = require("./src/constants");
const Game_1 = require("./src/game/Game");
const BetPlay_1 = require("./src/aviator/BetPlay");
const BetControl_1 = require("./src/aviator/BetControl");
(() => __awaiter(void 0, void 0, void 0, function* () {
    const aviatorPage = new BetPlay_1.AviatorBetPlay(constants_1.HomeBet.betplay.url);
    yield aviatorPage.open();
    const game = new Game_1.Game("demo", aviatorPage.multipliers, aviatorPage.balance, aviatorPage.minimumBet, aviatorPage.maximumBet, aviatorPage.maximumWinForOneBet);
    const sleepNow = (delay) => new Promise((resolve) => setTimeout(resolve, delay));
    while (true) {
        yield aviatorPage.waitNextGame();
        game.addMultiplier(aviatorPage.multipliers.slice(-1)[0]);
        const bets = game.getNextBet();
        if (bets.length) {
            console.log("bets:", bets);
            for (let index = 0; index < bets.length; index++) {
                const bet = bets[index];
                const control = index == 0 ? BetControl_1.Control.Control1 : BetControl_1.Control.Control2;
                yield aviatorPage.bet(bet.amount, bet.multiplier, control);
                yield sleepNow(2000);
            }
        }
    }
    // const average = game.getAverage(1)
    // await aviatorPage.bet(5, average, Control.Control2)
    // await aviatorPage._controls?.setAutoCashOut(2, Control.Control1)
    // await new_page.screenshot({ path: 'example.png' });
    // console.log("screenshot")
    // await browser.close();
}))();
//# sourceMappingURL=index.js.map