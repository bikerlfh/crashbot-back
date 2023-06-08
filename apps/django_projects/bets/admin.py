# Django
from django.contrib import admin

# Internal
from apps.django_projects.bets.models import Bet


class BetAdmin(admin.ModelAdmin):
    list_display = ["balance", "prediction", "status", "multiplier", "profit_amount"]
    list_filter = ["status"]
    readonly_fields = []

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Bet, BetAdmin)
