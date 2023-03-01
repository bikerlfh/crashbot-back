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
exports.BetControl = exports.Control = void 0;
var Control;
(function (Control) {
    Control[Control["Control1"] = 1] = "Control1";
    Control[Control["Control2"] = 2] = "Control2";
})(Control = exports.Control || (exports.Control = {}));
class BetControl {
    constructor(aviatorPage) {
        this._betControl_1 = null;
        this._betControl_2 = null;
        this._amountInput_1 = null;
        this._amountInput_2 = null;
        this._betSwitcherButton_1 = null;
        this._autoSwitcherButton_1 = null;
        this._betSwitcherButton_2 = null;
        this._autoSwitcherButton_2 = null;
        this._autoCashOutSwitcher_1 = null;
        this._autoCashOutSwitcher_2 = null;
        this._autoCashOutMultiplier_1 = null;
        this._autoCashOutMultiplier_2 = null;
        this._betButton_1 = null;
        this._betButton_2 = null;
        this.isActiveAutoCashOutControl_1 = false;
        this.isActiveAutoCashOutControl_2 = false;
        this.aviatorPage = aviatorPage;
        this.wasLoad = false;
    }
    _randomDelay() {
        const min = 15;
        const max = 50;
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    init() {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function* () {
            const bet_controls = this.aviatorPage.locator("app-bet-control");
            // app-navigation-switcher
            this._betControl_1 = bet_controls.first();
            this._betControl_2 = bet_controls.last();
            if (this._betControl_1 == null || this._betControl_2 == null) {
                throw "no bet controls";
            }
            const inputAppSpinner_1 = this._betControl_1.locator("app-spinner").first();
            const inputAppSpinner_2 = this._betControl_2.locator("app-spinner").first();
            if (inputAppSpinner_1 == null || inputAppSpinner_2 == null) {
                throw "no inputAppSpinner_1 or inputAppSpinner_2";
            }
            this._amountInput_1 = inputAppSpinner_1.locator("input").first();
            this._amountInput_2 = inputAppSpinner_2.locator("input").first();
            const appNavigationSwitcher_1 = this._betControl_1.locator("app-navigation-switcher").first();
            const appNavigationSwitcher_2 = this._betControl_2.locator("app-navigation-switcher").first();
            if (appNavigationSwitcher_1 == null) {
                throw "no appNavigationSwitcher_1";
            }
            if (appNavigationSwitcher_2 == null) {
                throw "no appNavigationSwitcher_2";
            }
            const buttons_1 = appNavigationSwitcher_1.locator("button");
            const buttons_2 = appNavigationSwitcher_2.locator("button");
            this._betSwitcherButton_1 = buttons_1.first();
            this._autoSwitcherButton_1 = buttons_1.last();
            this._betSwitcherButton_2 = buttons_2.first();
            this._autoSwitcherButton_2 = buttons_2.last();
            this._autoCashOutSwitcher_1 = this._betControl_1.locator("app-ui-switcher").first();
            this._autoCashOutSwitcher_2 = this._betControl_2.locator("app-ui-switcher").first();
            yield this._autoSwitcherButton_1.click({ delay: this._randomDelay() });
            yield this._autoSwitcherButton_2.click({ delay: this._randomDelay() });
            yield ((_a = this._autoCashOutSwitcher_1) === null || _a === void 0 ? void 0 : _a.click({ delay: this._randomDelay() }));
            yield ((_b = this._autoCashOutSwitcher_2) === null || _b === void 0 ? void 0 : _b.click({ delay: this._randomDelay() }));
            const cashOutSpinner_1 = this._betControl_1.locator(".cashout-spinner-wrapper").first();
            const cachOutSpinner_2 = this._betControl_2.locator(".cashout-spinner-wrapper").first();
            if (cashOutSpinner_1 == null) {
                throw "no cashOutSpinner_1";
            }
            if (cachOutSpinner_2 == null) {
                throw "no cachOutSpinner_2";
            }
            this._autoCashOutMultiplier_1 = cashOutSpinner_1.locator("input").first();
            this._autoCashOutMultiplier_2 = cachOutSpinner_2.locator("input").first();
            if (!this._autoCashOutMultiplier_1) {
                throw "no _autoCashOutMultiplier_1";
            }
            if (!this._autoCashOutMultiplier_2) {
                throw "no _autoCashOutMultiplier_2";
            }
            // this._betButton_1 = await this._betControl_1.$(".buttons-block>button")
            //this._betButton_2 = await this._betControl_2.$(".buttons-block>button")
            // app-bet-control.buttons-block>button
            const betButtons = this.aviatorPage.locator("button", { hasText: /\B\E\T/ });
            this._betButton_1 = betButtons.first();
            this._betButton_2 = betButtons.last();
            this.wasLoad = true;
        });
    }
    setAutoCashOut(multiplier, control) {
        return __awaiter(this, void 0, void 0, function* () {
            let autoCashOutMultiplier = this._autoCashOutMultiplier_1;
            if (control === Control.Control2) {
                autoCashOutMultiplier = this._autoCashOutMultiplier_2;
            }
            if (!autoCashOutMultiplier) {
                throw "buttons null autoCashOutMultiplier";
            }
            const value = parseFloat(parseFloat(yield autoCashOutMultiplier.inputValue({ timeout: 500 })).toFixed(0));
            if (value != multiplier) {
                yield autoCashOutMultiplier.fill("", { timeout: 500 });
                yield autoCashOutMultiplier.type(multiplier.toString(), { delay: 100 });
            }
        });
    }
    updateAmount(amount, control) {
        return __awaiter(this, void 0, void 0, function* () {
            let input = this._amountInput_1;
            if (control == Control.Control2) {
                input = this._amountInput_2;
            }
            if (input == null) {
                throw "updateAmount :: input null";
            }
            const value = parseFloat(parseFloat(yield input.inputValue({ timeout: 500 })).toFixed(0));
            if (value != amount) {
                yield input.fill("", { timeout: 500 });
                yield input.type(amount.toString(), { delay: 100 });
            }
            yield this.aviatorPage.waitForTimeout(500);
        });
    }
    bet(amount, multiplier, control) {
        return __awaiter(this, void 0, void 0, function* () {
            if (multiplier == null || amount == null) {
                throw "bet :: no multiplier or amount";
            }
            yield this.setAutoCashOut(multiplier, control);
            yield this.updateAmount(amount, control);
            if (this._betButton_1 == null || this._betButton_2 == null) {
                throw "bet: bet button null. control";
            }
            if (control === Control.Control1) {
                yield this._betButton_1.click();
                ({ delay: this._randomDelay() });
                yield this.aviatorPage.waitForTimeout(1000);
                return;
            }
            yield this._betButton_2.click({ delay: this._randomDelay() });
            yield this.aviatorPage.waitForTimeout(1000);
        });
    }
}
exports.BetControl = BetControl;
//# sourceMappingURL=BetControl.js.map