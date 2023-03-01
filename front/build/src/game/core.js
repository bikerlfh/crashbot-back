"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Bet = exports.Average = exports.Multiplier = exports.Player = void 0;
class Player {
    constructor(id, balance) {
        this.id = null;
        this.balance = 0;
        this.id = id;
        this.balance = balance;
    }
    updateBalance(amount) {
        // the amount can be negative
        this.balance += amount;
    }
}
exports.Player = Player;
class Multiplier {
    constructor(multiplier) {
        this.multiplier = multiplier;
        if (multiplier < 2) {
            this.category = 1;
        }
        else if (multiplier < 10) {
            this.category = 2;
        }
        else {
            this.category = 3;
        }
    }
}
exports.Multiplier = Multiplier;
class Average {
    constructor(category) {
        this.average = 0;
        this.totalMultiplier = 0;
        this.count = 0;
        this.percentage = 0;
        this.positions = [];
        this.category = category;
    }
}
exports.Average = Average;
class Bet {
    constructor(amount, multiplier) {
        this.amount = 0;
        this.multiplier = 0;
        this.profit = 0;
        this.amount = amount;
        this.multiplier = multiplier;
    }
    evaluate(lastMultiplier) {
        if (lastMultiplier >= this.multiplier) {
            this.profit += this.amount * (this.multiplier - 1);
        }
        else {
            this.profit -= this.amount;
        }
        return parseFloat(this.profit.toFixed(2));
    }
}
exports.Bet = Bet;
//# sourceMappingURL=core.js.map