# Django
from django.contrib import admin
from django.forms import CharField, ChoiceField, ModelForm

# Libraries
from apps.django_projects.predictions.constants import BotType
from apps.django_projects.predictions.models import Bot, BotStrategy
from apps.utils.tools import enum_to_choices


class BotAdmin(admin.ModelAdmin):
    class StrategyForm(ModelForm):
        bot_type = ChoiceField(choices=enum_to_choices(BotType))

        class Meta:
            model = Bot
            fields = "__all__"

    list_display = ["name", "bot_type", "is_active"]
    list_filter = ["bot_type", "is_active"]
    form = StrategyForm


class BotStrategyAdmin(admin.ModelAdmin):
    list_display = ["bot", "number_of_bets", "profit_percentage", "is_active"]
    list_filter = ["bot", "is_active"]


admin.site.register(Bot, BotAdmin)
admin.site.register(BotStrategy, BotStrategyAdmin)
