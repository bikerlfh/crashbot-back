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
exports.AviatorBetPlay = void 0;
const playwright_1 = __importDefault(require("playwright"));
const Aviator_1 = require("./Aviator");
const BetControl_1 = require("./BetControl");
class AviatorBetPlay extends Aviator_1.AviatorPage {
    open() {
        return __awaiter(this, void 0, void 0, function* () {
            this._browser = yield playwright_1.default.chromium.launch({ headless: false });
            this._context = yield this._browser.newContext();
            this._page = yield this._context.newPage();
            yield this._page.goto(this.url);
            yield this._page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", { timeout: 50000 });
            yield this._page.reload({ waitUntil: "domcontentloaded" });
            while (true) {
                try {
                    // gameFrame
                    // spribe-game
                    const frame = this._page.frameLocator("#gameFrame").frameLocator("#spribe-game");
                    if (frame == null) {
                        console.log("no frame");
                        continue;
                    }
                    console.log("frame: ", typeof (frame));
                    yield frame.locator(".result-history").waitFor({
                        timeout: 5000
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
}
exports.AviatorBetPlay = AviatorBetPlay;
//# sourceMappingURL=BetPlay.js.map