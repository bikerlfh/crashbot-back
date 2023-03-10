# Django
from django.contrib.auth.models import User
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
    number_of_players = models.SmallIntegerField(null=True)
    multiplier = models.DecimalField(max_digits=10, decimal_places=2)
    multiplier_dt = models.DateTimeField()

    class Meta:
        db_table = "homebet_multiplier"


class Customer(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, related_name="customer"
    )
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = "customer"


class CustomerBalance(BaseModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, related_name="balances"
    )
    username = models.CharField(max_length=50, null=True, blank=True)
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.DO_NOTHING, related_name="balances"
    )
    currency = models.ForeignKey(
        Currency, on_delete=models.DO_NOTHING, related_name="customers"
    )
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=2)

    class Meta:
        db_table = "customer_balance"


class CustomerBetHistory(BaseModel):
    balance = models.ForeignKey(
        CustomerBalance,
        on_delete=models.DO_NOTHING,
        related_name="bet_history",
    )
    bet_amount = models.DecimalField(max_digits=18, decimal_places=2)
    multiplier = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    profit_amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = "customer_bet_history"
