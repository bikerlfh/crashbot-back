from django.contrib import admin
from apps.django_projects.core.models import (
    Currency,
    HomeBet,
    Customer,
    CustomerBalance
)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]


class HomeBetAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "min_bet", "max_bet"]
    fields = ["name", "url", "min_bet", "max_bet", "currencies"]


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ["customer", "username", "home_bet", "amount"]


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(HomeBet, HomeBetAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerBalance, CustomerBalanceAdmin)
