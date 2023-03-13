from django.db import models

from apps.django_projects.bets.constants import BetStatus
from apps.utils.django.models import BaseModel
from apps.django_projects.customers.models import CustomerBalance


class Bet(BaseModel):
    balance = models.ForeignKey(
        CustomerBalance,
        on_delete=models.DO_NOTHING,
        related_name="bets",
    )
    external_id = models.CharField(
        max_length=50
    )
    prediction = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    prediction_round = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    multiplier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True
    )
    multiplier_result = models.DecimalField(
        max_digits=18, decimal_places=2,
        null=True,
        blank=True
    )
    profit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=10,
        default=BetStatus.PENDING.value
    )

    class Meta:
        db_table = "bet"
        unique_together = ("balance", "external_id")
