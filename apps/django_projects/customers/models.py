# Django
from django.contrib.auth.models import User
from django.db import models

# Internal
from apps.django_projects.core.models import HomeBet, Plan
from apps.utils.django.models import BaseModel, BaseModelUUID


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


class CustomerPlan(BaseModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, related_name="plans"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.DO_NOTHING, related_name="customer_plans"
    )
    start_dt = models.DateField()
    end_dt = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "customer_plan"

    def __str__(self):
        return f"{self.customer} - {self.plan}"


class CustomerSession(BaseModelUUID):
    customer = models.ForeignKey(
        Customer, on_delete=models.DO_NOTHING, related_name="sessions"
    )
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.DO_NOTHING, related_name="sessions"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("customer", "home_bet", "is_active")
        db_table = "customer_session"
