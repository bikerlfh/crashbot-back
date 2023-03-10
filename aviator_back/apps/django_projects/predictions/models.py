from decimal import Decimal
from django.db import models
from apps.utils.django.models import BaseModel

from apps.django_projects.core.models import HomeBet
from apps.prediction.constants import ModelType, Category
from apps.utils.tools import enum_to_choices


class ModelHomeBet(BaseModel):
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.PROTECT, related_name='models'
    )
    name = models.CharField(max_length=50)
    model_type = models.CharField(
        max_length=25,
        choices=enum_to_choices(ModelType)
    )
    length_window = models.SmallIntegerField(
        default=10
    )
    average_predictions = models.DecimalField(
        default=Decimal(0),
        max_digits=5,
        decimal_places=2
    )
    average_bets = models.DecimalField(
        default=Decimal(0),
        max_digits=5,
        decimal_places=2
    )
    others = models.JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "model_homebet"


class ModelAverageResult(BaseModel):
    model_home_bet = models.ForeignKey(
        ModelHomeBet, on_delete=models.PROTECT, related_name='averages'
    )
    result_date = models.DateTimeField()
    category = models.SmallIntegerField(
        choices=enum_to_choices(Category)
    )  # 1, 2, 3
    correct_predictions = models.IntegerField(default=0)
    incorrect_predictions = models.IntegerField(default=0)
    average_predictions = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    correct_bets = models.IntegerField(default=0)
    incorrect_bets = models.IntegerField(default=0)
    average_bets = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    other_info = models.JSONField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "model_average_result"

    @property
    def total_predictions(self) -> int:
        return self.correct_predictions + self.incorrect_predictions
