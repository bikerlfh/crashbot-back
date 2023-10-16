# Django
from django.db import models

# Internal
from apps.django_projects.core.models import HomeBet
from apps.django_projects.predictions.constants import (
    BotType,
    ConditionAction,
    ConditionON,
    ModelStatus,
)
from apps.prediction.constants import Category, ModelType
from apps.utils.django.models import BaseModel
from apps.utils.tools import enum_to_choices


class ModelHomeBet(BaseModel):
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.PROTECT, related_name="models"
    )
    name = models.CharField(max_length=50, unique=True)
    model_type = models.CharField(
        max_length=25, choices=enum_to_choices(ModelType)
    )
    status = models.CharField(
        max_length=10,
        choices=enum_to_choices(ModelStatus),
        default=ModelStatus.ACTIVE.value,
    )
    seq_len = models.SmallIntegerField(default=10)
    average_predictions = models.FloatField(default=0)
    average_bets = models.FloatField(default=0)
    result_date = models.DateTimeField(null=True, blank=True, default=None)
    others = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "model_homebet"
        unique_together = ("home_bet", "model_type")


class ModelCategoryResult(BaseModel):
    model_home_bet = models.ForeignKey(
        ModelHomeBet, on_delete=models.PROTECT, related_name="category_results"
    )
    category = models.SmallIntegerField(
        choices=enum_to_choices(Category)
    )  # 1, 2, 3
    correct_predictions = models.IntegerField(default=0)
    incorrect_predictions = models.IntegerField(default=0)
    percentage_predictions = models.FloatField()
    correct_bets = models.IntegerField(default=0)
    incorrect_bets = models.IntegerField(default=0)
    percentage_bets = models.FloatField()
    other_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "model_category_result"

    @property
    def total_predictions(self) -> int:
        return self.correct_predictions + self.incorrect_predictions


class Bot(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    bot_type = models.CharField(
        max_length=15,
        default=BotType.LOOSE.value,
    )
    is_active = models.BooleanField(default=True)
    risk_factor = models.FloatField(default=0.1)
    min_multiplier_to_bet = models.FloatField(
        default=1.5, help_text="Minimum multiplier to bet"
    )
    min_multiplier_to_recover_losses = models.FloatField(
        default=2.0, help_text="Minimum multiplier to recover losses"
    )
    min_probability_to_bet = models.FloatField(
        default=0.65, help_text="Minimum probability to bet"
    )
    min_category_percentage_to_bet = models.FloatField(
        default=0,
        help_text="Minimum percentage of correct predictions by category",
    )
    max_recovery_percentage_on_max_bet = models.FloatField(
        default=0.5,
        help_text="Maximum recovery percentage on maximum bet of home bet",
    )
    min_average_model_prediction = models.FloatField(
        default=0, help_text="Minimum average prediction model in live to bet"
    )
    stop_loss_percentage = models.FloatField(
        default=0, help_text="Stop loss percentage"
    )
    take_profit_percentage = models.FloatField(
        default=0, help_text="Take profit percentage"
    )

    class Meta:
        db_table = "bot"

    def __str__(self):
        return self.name


class BotCondition(BaseModel):
    bot = models.ForeignKey(
        Bot, on_delete=models.PROTECT, related_name="conditions"
    )
    condition_on = models.CharField(
        max_length=30,
        choices=enum_to_choices(ConditionON),
        default=ConditionON.EVERY_WIN.value,
    )
    condition_on_value = models.FloatField(default=0)
    condition_on_value_2 = models.FloatField(
        null=True, blank=True, default=None
    )
    condition_action = models.CharField(
        max_length=25,
        choices=enum_to_choices(ConditionAction),
        default=ConditionAction.UPDATE_MULTIPLIER.value,
    )
    action_value = models.FloatField(default=0)
    others = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "bot_condition"
        unique_together = (
            "bot",
            "condition_on",
            "condition_on_value",
            "condition_action",
        )
