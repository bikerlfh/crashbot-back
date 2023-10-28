from jsoneditor.forms import JSONEditor

# Django
from django.contrib import admin
from django.forms import ChoiceField, ModelForm
from django.db.models.fields.json import JSONField

# Internal
from apps.utils.django.admin.models import ModelAdmin
from apps.django_projects.predictions.constants import BotType
from apps.django_projects.predictions.models import (
    Bot,
    BotCondition,
    ModelHomeBet,
)
from apps.utils.tools import enum_to_choices


DESCRIPTION_ACTIONS = """
<br>This section contains the JSON information for "actions".
Please review the provided documentation for detailed guidelines:
Follow this JSON structure:
<pre>
[
    {
        "condition_action": str,
        "action_value": float
    },
    {
        "condition_action": str,
        "action_value": float
    }
]
</pre><br>
"""


@admin.register(Bot)
class BotAdmin(ModelAdmin):
    class StrategyForm(ModelForm):
        bot_type = ChoiceField(choices=enum_to_choices(BotType))

        class Meta:
            model = Bot
            fields = "__all__"

    list_display = ["name", "bot_type", "is_active"]
    list_filter = ["bot_type", "is_active"]
    form = StrategyForm


@admin.register(BotCondition)
class BotConditionAdmin(ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    list_display = [
        "bot",
        "condition_on",
        "condition_on_value",
        # "condition_action",
        # "action_value",
    ]
    list_filter = ["bot", "condition_on"]
    # fields = [
    #     "bot",
    #     "condition_on",
    #     "condition_on_value",
    #     "condition_on_value_2",
    #     "others",
    #     "actions",
    # ]
    # raw_id_fields = ["bot"]
    fieldsets = (
        (
            "REQUIRED INFORMATION",
            {
                "fields": (
                    "bot",
                    "condition_on",
                    "condition_on_value",
                    "condition_on_value_2",
                    # "others",
                ),
            },
        ),
        (
            "ACTIONS JSON",
            {
                "fields": ("actions",),
                "classes": ("collapse",),
                "description": DESCRIPTION_ACTIONS,
            },
        ),
    )


@admin.register(ModelHomeBet)
class ModelHomeBetAdmin(ModelAdmin):
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
