# Django
from django.db import models

# Internal
from apps.utils.django.models import BaseModel


class Currency(BaseModel):
    code = models.CharField(max_length=3, unique=True)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "currency"


class HomeBet(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    min_bet = models.DecimalField(max_digits=18, decimal_places=2)
    max_bet = models.DecimalField(max_digits=18, decimal_places=2)
    currencies = models.ManyToManyField(Currency)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "homebet"


class HomeBetMultiplier(BaseModel):
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.DO_NOTHING, related_name="multipliers"
    )
    multiplier = models.DecimalField(max_digits=10, decimal_places=2)
    multiplier_dt = models.DateTimeField()

    class Meta:
        db_table = "homebet_multiplier"
        indexes = [
            models.Index(fields=["home_bet", "multiplier_dt"]),
        ]


class Plan(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        related_name="plans",
        on_delete=models.DO_NOTHING
    )
    duration_in_days = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "plan"

    def __str__(self):
        return self.name
