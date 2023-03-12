from django.contrib.auth.models import User
from django.db import models

from apps.django_projects.bets.constants import BetStatus
from apps.utils.django.models import BaseModel
from apps.django_projects.core.models import HomeBet
from apps.utils.cryptography_tool import FernetCrypto


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
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.DO_NOTHING, related_name="balances"
    )
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=2)

    class Meta:
        db_table = "customer_balance"
        unique_together = ("customer", "home_bet")

    def save(self, *args, **kwargs):
        self.password = FernetCrypto.encrypt(str(self.password))
        super().save(*args, **kwargs)

    def get_password(self):
        return FernetCrypto.decrypt(self.password)


class Bet(BaseModel):
    balance = models.ForeignKey(
        CustomerBalance,
        on_delete=models.DO_NOTHING,
        related_name="bets",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    multiplier = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    profit_amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(
        max_length=10,
        default=BetStatus.PENDING.value
    )

    class Meta:
        db_table = "bet"

