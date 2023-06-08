# Django
from django.contrib.auth.models import User
from django.db import models

# Internal
from apps.django_projects.core.models import HomeBet
from apps.utils.django.models import BaseModel


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
    amount = models.DecimalField(default=0, max_digits=18, decimal_places=2)

    class Meta:
        db_table = "customer_balance"
        unique_together = ("customer", "home_bet")

    def __str__(self):
        return f"{self.customer} - {self.home_bet}"
