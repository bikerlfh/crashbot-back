# Django
from django.contrib import admin

# Internal
from apps.django_projects.core.models import Currency, HomeBet, Plan


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]


@admin.register(HomeBet)
class HomeBetAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "min_bet", "max_bet"]
    fields = ["name", "url", "min_bet", "max_bet", "currencies"]


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
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
        "is_active",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name"]
        return []
