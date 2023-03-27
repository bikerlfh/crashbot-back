# Django
from django.contrib import admin
from django.forms import CharField, ModelForm, ChoiceField

# Internal
from apps.django_projects.predictions.models import PlayerStrategy
from apps.django_projects.predictions.constants import StrategyType
from apps.utils.tools import enum_to_choices


class PlayerStrategyAdmin(admin.ModelAdmin):
    class StrategyForm(ModelForm):
        strategy_type = ChoiceField(choices=enum_to_choices(StrategyType))

        class Meta:
            model = PlayerStrategy
            fields = "__all__"

    list_display = ["strategy_type", "number_of_bets", "profit_percentage", "is_active"]
    list_filter = ["strategy_type", "is_active"]
    form = StrategyForm


admin.site.register(PlayerStrategy, PlayerStrategyAdmin)
