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


class CrashGame(BaseModel):
    name = models.CharField(max_length=25, unique=True)

    class Meta:
        db_table = "crash_game"

    def __str__(self):
        return self.name


class HomeBet(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField()
    # min_bet = models.DecimalField(max_digits=18, decimal_places=2)
    # max_bet = models.DecimalField(max_digits=18, decimal_places=2)
    # currencies = models.ManyToManyField(Currency)
    # amount_multiple = models.FloatField(default=100.0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "homebet"


class HomeBetGame(BaseModel):
    home_bet = models.ForeignKey(
        HomeBet, on_delete=models.DO_NOTHING, related_name="games"
    )
    crash_game = models.ForeignKey(
        CrashGame, on_delete=models.DO_NOTHING, related_name="home_bets"
    )
    limits = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.home_bet} {self.crash_game}"

    class Meta:
        db_table = "home_bet_game"
        unique_together = (
            "home_bet",
            "crash_game",
        )


class Multiplier(BaseModel):
    home_bet_game = models.ForeignKey(
        HomeBetGame, related_name="multipliers", on_delete=models.DO_NOTHING
    )
    multiplier = models.DecimalField(max_digits=10, decimal_places=2)
    multiplier_dt = models.DateTimeField()

    class Meta:
        db_table = "home_bet_multiplier"
        indexes = [
            models.Index(fields=["home_bet_game", "multiplier_dt"]),
        ]


class CrashApp(BaseModel):
    hash_str = models.CharField(max_length=100)
    name = models.CharField(max_length=50, unique=True)
    home_bet_games = models.ManyToManyField(
        HomeBetGame, related_name="crash_apps"
    )
    version = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "crash_app"

    def __str__(self):
        return f"{self.name} ({self.version})"


class Plan(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey(
        Currency, related_name="plans", on_delete=models.DO_NOTHING
    )
    duration_in_days = models.IntegerField()
    with_ai = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    crash_apps = models.ManyToManyField(CrashApp, related_name="plans")

    class Meta:
        db_table = "plan"

    def __str__(self):
        return self.name
