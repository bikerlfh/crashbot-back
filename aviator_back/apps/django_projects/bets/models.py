# Django
from django.db import models

# Libraries
from apps.django_projects.bets.constants import BetStatus, BetType
from apps.django_projects.customers.models import CustomerBalance
from apps.utils.django.models import BaseModel


class Bet(BaseModel):
    balance = models.ForeignKey(
        CustomerBalance,
        on_delete=models.DO_NOTHING,
        related_name="bets",
    )
    external_id = models.CharField(max_length=50)
    prediction = models.FloatField(default=0.0)
    amount = models.FloatField()
    multiplier = models.FloatField(null=True)
    multiplier_result = models.FloatField(null=True, blank=True)
    profit_amount = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, default=BetStatus.PENDING.value)
    bet_type = models.CharField(max_length=10, default=BetType.AUTOMATIC.value)

    class Meta:
        db_table = "bet"
        unique_together = ("balance", "external_id")

    @property
    def prediction_round(self) -> int:
        return round(self.prediction_round, 0)
