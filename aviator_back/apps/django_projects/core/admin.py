# Django
from django.contrib import admin

# Libraries
from apps.django_projects.core.models import Currency, HomeBet


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]


class HomeBetAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "min_bet", "max_bet"]
    fields = ["name", "url", "min_bet", "max_bet", "currencies"]


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(HomeBet, HomeBetAdmin)
