# Standard Library
from typing import Optional

# Libraries
import numpy as np

# Internal
from apps.django_projects.core import selectors as core_selectors
from apps.django_projects.predictions import selectors as prediction_selectors
from apps.django_projects.predictions.constants import ModelStatus
from apps.prediction import utils as prediction_utils
from apps.prediction.models.main import CoreModel


def simulate_game(
    home_bet_id: int,
    bankroll: float,
    max_amount_bet: float,
    model_home_bet_id: Optional[int] = None,
    max_count_multipliers: Optional[int] = 200,
) -> list[dict[str, any]]:
    max_bet_amount = 50000
    home_bet = core_selectors.filter_home_bet(home_bet_id=home_bet_id).first()
    if not home_bet:
        print("Home bet not found")
        return
    multipliers = core_selectors.get_last_multipliers(
        home_bet_id=home_bet_id, count=max_count_multipliers
    )
    if not multipliers:
        print("Multipliers not found")
        return
    data_result = []
    min_amount_bet = round(max_amount_bet / 3, 0)
    multiplier_control_1 = 2
    multiplier_control_2 = 2
    amount_remaining = bankroll
    filter_ = dict(
        home_bet_id=home_bet_id,
        status=ModelStatus.ACTIVE,
    )
    if model_home_bet_id:
        filter_["id"] = model_home_bet_id
    models = prediction_selectors.filter_model_home_bet(**filter_)
    if not models:
        print("Models not found")
        return
    for model in models:
        model_ = CoreModel(model_home_bet=model)
        data = prediction_utils.transform_multipliers_to_data(
            multipliers=multipliers
        )
        X, y = model_.model._split_data_to_train(data)  # NOQA
        y_multiplier = np.array(multipliers[model.seq_len :])
        bets_won = 0
        bets_lost = 0
        total_profit = 0
        max_loss = 0
        amounts_lost = []
        for i in range(len(X)):
            if i == len(X) - 1:
                break
            _max_amount_bet = max_amount_bet
            _min_amount_bet = min_amount_bet
            _multiplier_control_1 = multiplier_control_1
            _data = X[i]
            # next_value = y[i]
            next_multiplier = y_multiplier[i]
            prediction_data = model_.model.predict(data=_data)
            # value = prediction_data.prediction
            value_round = prediction_data.prediction_round

            if value_round < 2:
                continue
            probability = prediction_data.probability
            if probability < 0.69:
                continue
            amount_to_recover = 0
            if total_profit < 0:
                amount_to_recover = abs(total_profit)
                max_amount_to_recover = max_bet_amount * 0.5
                if amount_to_recover > max_amount_to_recover:
                    amount_to_recover = max_amount_to_recover
                _max_amount_bet = amount_to_recover
                _multiplier_control_1 = 2
                _min_amount_bet = 0

            # print(f"value_round: {value_round}, next_multiplier: {next_multiplier}")
            if value_round < next_multiplier:
                bets_won += 1
                profit = _max_amount_bet * (_multiplier_control_1 - 1)
                profit += _min_amount_bet * (multiplier_control_2 - 1)
                total_profit = 0
                # total_profit += profit
                amount_remaining += profit
            else:
                bets_lost += 1
                total_profit -= _max_amount_bet
                total_profit -= _min_amount_bet
                amounts_lost.append(_max_amount_bet)
                amounts_lost.append(_min_amount_bet)
                amount_remaining -= _max_amount_bet
                amount_remaining -= _min_amount_bet

            if total_profit < 0:
                amount_to_recover_ = abs(total_profit)
                if max_loss < amount_to_recover_:
                    max_loss = amount_to_recover_

            print(
                f"value_round: {value_round},"
                f" next_multiplier: {next_multiplier}, "
                f"amount_remaining: {amount_remaining}, "
                f"max_loss: {max_loss}, "
                f"amount_to_recover: {amount_to_recover}"
            )

            if amount_remaining <= 0:
                break
        data_result.append(
            dict(
                model_id=model.id,
                amount_remaining=amount_remaining,
                bets_won=bets_won,
                bets_lost=bets_lost,
                max_loss=max_loss,
            )
        )
    return data_result
