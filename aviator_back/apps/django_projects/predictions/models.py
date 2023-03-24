# Standard Library

# Django
from django.db import models

# Internal
from apps.django_projects.core.models import HomeBet
from apps.django_projects.predictions.constants import ModelStatus
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
    status = models.CharField(max_length=10, default=ModelStatus.ACTIVE.value)
    seq_len = models.SmallIntegerField(default=10)
    average_predictions = models.FloatField(default=0)
    average_bets = models.FloatField(default=0)
    result_date = models.DateTimeField(null=True, blank=True, default=None)
    others = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "model_homebet"


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
