# Django
from django.contrib import admin

# Internal
from apps.django_projects.customers.models import Customer, CustomerBalance


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ["customer", "home_bet", "amount"]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerBalance, CustomerBalanceAdmin)
