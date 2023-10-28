from jsoneditor.forms import JSONEditor

# Django
from django.contrib import admin
from django.db.models.fields.json import JSONField

# Internal
from apps.utils.django.admin.models import ModelAdmin
from apps.utils import cryptography_tool
from apps.django_projects.core.models import (
    Currency,
    HomeBet,
    HomeBetGame,
    Plan,
    CrashApp,
    CrashGame,
)


LIMITS_DESCRIPTION = """
<br>This section contains the JSON information for "limits".
Please review the provided documentation for detailed guidelines:
Follow this JSON structure:
<pre>
{
    "COP": {
        "min_bet": 500,
        "max_bet": 500000,
        "amount_multiple": 100.0
    },
    "USD": {
        "min_bet": 1,
        "max_bet": 100,
        "amount_multiple": 1.0
    }
}
</pre><br>
"""


@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ["code", "description"]


@admin.register(HomeBet)
class HomeBetAdmin(ModelAdmin):
    list_display = ["name", "url"]
    fields = ["name", "url"]


@admin.register(CrashGame)
class CrashGameAdmin(ModelAdmin):
    list_display = ["name"]
    fields = ["name"]


@admin.register(HomeBetGame)
class HomeBetGameAdmin(ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    list_display = ["home_bet", "crash_game"]
    search_fields = ["home_bet", "crash_game"]
    list_filter = ["home_bet", "crash_game"]
    # fields = ["home_bet", "crash_game", "limits"]

    fieldsets = (
        (
            "REQUIRED INFORMATION",
            {
                "fields": (
                    "home_bet",
                    "crash_game",
                ),
            },
        ),
        (
            "LIMITS JSON",
            {
                "fields": ("limits",),
                "classes": ("collapse",),
                "description": LIMITS_DESCRIPTION,
            },
        ),
    )


@admin.register(CrashApp)
class CrashAppAdmin(ModelAdmin):
    list_display = ["name", "version", "is_active"]
    fields = ["hash_str", "name", "home_bet_games", "version", "is_active"]
    # raw_id_fields = ["home_bet_games"]
    readonly_fields = ["hash_str"]

    def save_model(self, request, obj, form, change):
        obj.hash_str = cryptography_tool.md5(f"{obj.name}{obj.version}")
        super().save_model(request, obj, form, change)


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = [
        "name",
        "description",
        "price",
        "currency",
        "duration_in_days",
        "with_ai",
        "is_active",
    ]
    fields = [
        "name",
        "description",
        "price",
        "currency",
        "duration_in_days",
        "with_ai",
        "crash_apps",
        "is_active",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        return []
