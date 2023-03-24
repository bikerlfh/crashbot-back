# Django
from django.contrib import admin
from django.forms import CharField, ModelForm, PasswordInput

# Internal
from apps.django_projects.customers.models import Customer, CustomerBalance


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


class CustomerBalanceAdmin(admin.ModelAdmin):
    class BalanceForm(ModelForm):
        password = CharField(widget=PasswordInput(render_value=True))

        class Meta:
            model = CustomerBalance
            fields = "__all__"

    list_display = ["customer", "username", "home_bet", "amount"]
    form = BalanceForm


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerBalance, CustomerBalanceAdmin)
