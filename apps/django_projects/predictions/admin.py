# Django
from django.contrib import admin
from django.forms import ChoiceField, ModelForm

# Internal
from apps.django_projects.predictions.constants import BotType
from apps.django_projects.predictions.models import (
    Bot,
    BotStrategy,
    ModelHomeBet,
)
from apps.utils.tools import enum_to_choices


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    class StrategyForm(ModelForm):
        bot_type = ChoiceField(choices=enum_to_choices(BotType))

        class Meta:
            model = Bot
            fields = "__all__"

    list_display = ["name", "bot_type", "is_active"]
    list_filter = ["bot_type", "is_active"]
    form = StrategyForm


@admin.register(BotStrategy)
class BotStrategyAdmin(admin.ModelAdmin):
    list_display = ["bot", "number_of_bets", "profit_percentage", "is_active"]
    list_filter = ["bot", "is_active"]


@admin.register(ModelHomeBet)
class ModelHomeBetAdmin(admin.ModelAdmin):
    list_display = [
        "home_bet",
        "model_type",
        "status",
        "average_predictions",
        "result_date",
    ]
    list_filter = ["home_bet", "model_type", "status"]
    readonly_fields = [
        "name",
        "home_bet",
        "model_type",
        "seq_len",
        "average_predictions",
        "average_bets",
        "result_date",
        "others",
    ]

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

