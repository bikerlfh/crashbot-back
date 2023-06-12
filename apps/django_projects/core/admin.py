# Django
from django.contrib import admin

# Internal
from apps.django_projects.core.models import Currency, HomeBet


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]


@admin.register(HomeBet)
class HomeBetAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "min_bet", "max_bet"]
    fields = ["name", "url", "min_bet", "max_bet", "currencies"]
