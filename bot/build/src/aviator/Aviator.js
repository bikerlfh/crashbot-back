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
exports.AviatorPage = void 0;
const playwright_1 = __importDefault(require("playwright"));
const BetControl_1 = require("./BetControl");
class AviatorPage {
    constructor(url, isDemo = false) {
        this._browser = null;
        this._context = null;
        this._page = null;
        this._historyGame = null;
        this._balanceElement = null;
        this._controls = null;
        this.isDemo = false;
        this.minimumBet = 0;
        this.maximumBet = 0;
        this.maximumWinForOneBet = 0;
        this.multipliers = [];
        this.url = url;
        this.isDemo = isDemo;
        this.balance = 0;
    }
    open() {
        return __awaiter(this, void 0, void 0, function* () {
            this._browser = yield playwright_1.default.chromium.launch({ headless: false });
            this._context = yield this._browser.newContext();
            this._page = yield this._context.newPage();
            yield this._page.goto(this.url);
            if (this.isDemo) {
                yield this._page.getByRole('button', { name: 'Play Demo' }).click();
                yield this._page.getByRole('button', { name: "Yes I’m over 18" }).click();
                yield this._page.waitForTimeout(2000);
                let pages = this._context.pages();
                this._page = pages[1];
            }
            while (true) {
                try {
                    yield this._page.locator(".result-history").waitFor({
                        timeout: 30000
                    });
                    break;
                }
                catch (e) {
                    if (e instanceof playwright_1.default.errors.TimeoutError) {
                        console.log("error timeout");
                        continue;
                    }
                    throw e;
                }
            }
            this._historyGame = yield this._page.$(".result-history");
            console.log("result history found");
            this._controls = new BetControl_1.BetControl(this._page);
            yield this._controls.init();
            yield this.readBalance();
            yield this.readMultipliers();
            yield this.readGameLimits();
            console.log("aviator loaded");
        });
    }
    readGameLimits() {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            if (this._page == null) {
                throw "no page";
            }
            const menu = yield this._page.$(".dropdown-toggle.user");
            if (menu == null) {
                throw "no menu";
            }
            yield menu.click();
            yield this._page.waitForTimeout(400);
            const appUserMenu = yield this._page.$("app-user-menu-dropdown");
            if (appUserMenu == null) {
                throw "appusermenu is null";
            }
            const listMenu = (yield appUserMenu.$$(".list-menu")).slice(-1)[0];
            const menuLimits = (yield listMenu.$$(".list-menu-item")).slice(-1)[0];
            yield menuLimits.click();
            yield this._page.waitForTimeout(400);
            const limits = yield this._page.$$("app-game-limits ul>li>span");
            this.minimumBet = parseFloat(((_a = (yield limits[0].textContent())) === null || _a === void 0 ? void 0 : _a.split(" ")[0]) || "0");
            this.maximumBet = parseFloat(((_b = (yield limits[1].textContent())) === null || _b === void 0 ? void 0 : _b.split(" ")[0]) || "0");
            this.maximumWinForOneBet = parseFloat(((_c = (yield limits[2].textContent())) === null || _c === void 0 ? void 0 : _c.split(" ")[0]) || "0");
            const buttonClose = yield this._page.$("ngb-modal-window");
            yield (buttonClose === null || buttonClose === void 0 ? void 0 : buttonClose.click());
            console.log("minimumBet: ", this.minimumBet);
            console.log("maximumBet: ", this.maximumBet);
            console.log("maximumWinForOneBet: ", this.maximumWinForOneBet);
        });
    }
    readBalance() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._page == null) {
                throw "readBalance :: page is null";
            }
            this._balanceElement = yield this._page.$(".balance>.amount");
            if (this._balanceElement != null) {
                this.balance = parseFloat((yield this._balanceElement.textContent()) || "0");
                console.log("balance: ", this.balance);
            }
            return this.balance;
        });
    }
    readMultipliers() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._page && this._historyGame) {
                let items = yield this._historyGame.$$('app-payout-item');
                items.slice().reverse().forEach((item) => __awaiter(this, void 0, void 0, function* () {
                    const multiplier = yield item.textContent();
                    if (multiplier !== null) {
                        const value = parseFloat(multiplier.replace(/\s/g, '').replace("x", ""));
                        this.multipliers.push(value);
                    }
                }));
                yield this._page.waitForTimeout(2000);
            }
        });
    }
    bet(amount, multiplier, control) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._controls == null) {
                throw "AviatorPage :: no _controls";
            }
            this._controls.bet(amount, multiplier, control);
        });
    }
    waitNextGame() {
        return __awaiter(this, void 0, void 0, function* () {
            if (this._historyGame == null) {
                throw "waitNextGame :: no historyGame";
            }
            while (true) {
                try {
                    const len_multipliers = this.multipliers.length - 1;
                    let locator = yield this._historyGame.$('app-payout-item');
                    if (locator == null) {
                        continue;
                    }
                    const last_multiplier = parseFloat((yield locator.textContent()) || "0");
                    if (last_multiplier == null) {
                        continue;
                    }
                    if (this.multipliers[len_multipliers] != last_multiplier) {
                        this.multipliers.push(last_multiplier);
                        return;
                    }
                }
                catch (e) {
                    if (e instanceof playwright_1.default.errors.TimeoutError) {
                        console.log("error timeout");
                    }
                }
            }
        });
    }
}
exports.AviatorPage = AviatorPage;
//# sourceMappingURL=Aviator.js.map