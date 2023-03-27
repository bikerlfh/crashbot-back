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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const playwright_1 = __importDefault(require("playwright"));
const constants_1 = require("./src/constants");
const Game_1 = require("./src/game/Game");
(() => __awaiter(void 0, void 0, void 0, function* () {
    const browser = yield playwright_1.default.chromium.launch({ headless: false });
    const context = yield browser.newContext();
    const page = yield context.newPage();
    //page.on('domcontentloaded', (p) => console.log(`Loaded ${p.url()}`));
    yield page.goto(constants_1.URL_AVIATOR_DEMO);
    yield page.getByRole('button', { name: 'Play Demo' }).click();
    yield page.getByRole('button', { name: "Yes I’m over 18" }).click();
    yield page.waitForTimeout(2000);
    let pages = context.pages();
    const page_game = pages[1];
    const multipiers = [];
    let balance = 0;
    let history_games;
    // await page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", {timeout: 50000})
    while (true) {
        try {
            yield page_game.locator('.result-history').waitFor({
                timeout: 50000
            });
            break;
        }
        catch (e) {
            if (e instanceof playwright_1.default.errors.TimeoutError) {
                console.log("error timeout");
                return;
            }
        }
    }
    history_games = yield page_game.$('.result-history');
    console.log("result history found");
    // Get games history from tag app-payout-item
    if (history_games != null) {
        let items = yield history_games.$$('app-payout-item');
        items.slice().reverse().forEach((item) => __awaiter(void 0, void 0, void 0, function* () {
            const multiplier = yield item.textContent();
            if (multiplier !== null) {
                const value = parseFloat(multiplier.replace(/\s/g, '').replace("x", ""));
                multipiers.push(value);
            }
        }));
        yield page.waitForTimeout(2000);
    }
    if (history_games == null) {
        return;
    }
    // bet controls
    const bet_controls = yield page_game.$$("app-bet-control");
    const bet_control_1 = yield bet_controls[0].$("app-navigation-switcher");
    const bet_control_2 = yield bet_controls[1].$("app-navigation-switcher");
    const game = new Game_1.Game("test", multipiers, null);
    console.log("last multiplier: " + multipiers[multipiers.length - 1]);
    console.log("average 1:" + game.getAverage(1));
    console.log("average 2:" + game.getAverage(2));
    console.log("average 3:" + game.getAverage(3));
    while (true) {
        try {
            const len_multipliers = multipiers.length - 1;
            let locator = yield history_games.$('app-payout-item');
            if (locator == null) {
                continue;
            }
            const last_multiplier = parseFloat((yield locator.textContent()) || "0");
            if (last_multiplier == null) {
                continue;
            }
            if (multipiers[len_multipliers] != last_multiplier) {
                multipiers.push(last_multiplier);
                game.addMultiplier(last_multiplier);
                const balance_element = yield page_game.$(".balance>.amount");
                if (balance_element != null) {
                    balance = parseFloat((yield balance_element.textContent()) || "0");
                }
                console.log("changed " + last_multiplier + "; balance: " + balance);
                console.log("average 1:" + game.getAverage(1));
                console.log("average 2:" + game.getAverage(2));
                console.log("average 3:" + game.getAverage(3));
            }
        }
        catch (e) {
            if (e instanceof playwright_1.default.errors.TimeoutError) {
                console.log("error timeout");
            }
        }
    }
    // await new_page.screenshot({ path: 'example.png' });
    // console.log("screenshot")
    //await browser.close();
}))();
