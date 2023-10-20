# Standard Library
from datetime import datetime, timedelta

# Django
from django import forms
from django.contrib import admin

# Internal
from apps.django_projects.core.models import HomeBet
from apps.django_projects.customers import selectors, services
from apps.django_projects.customers.models import (
    Customer,
    CustomerBalance,
    CustomerPlan,
)


class CustomerAddForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    home_bets = forms.MultipleChoiceField(
        choices=[(h.id, h.name) for h in HomeBet.objects.all()], required=True
    )
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    repeat_password = forms.CharField(
        widget=forms.PasswordInput, required=False
    )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = Customer
        fields = (
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "home_bets",
            "password",
            "repeat_password",
        )
        readonly_fields = ["username"]

    def clean_username(self):
        instance = self.instance
        username = self.cleaned_data.get("username")
        user = selectors.filter_user_by_username(username=username).first()
        if not instance and user:
            raise forms.ValidationError("Username already exists")
        return username

    def clean_email(self):
        instance = self.instance
        email = self.cleaned_data.get("email")
        user = selectors.filter_user_by_email(email=email).first()
        if not instance and user:
            raise forms.ValidationError("Email already exists")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number:
            raise forms.ValidationError("Phone number is required")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.instance and not password:
            raise forms.ValidationError("Password is required")
        return password

    def clean_repeat_password(self):
        password = self.cleaned_data.get("password")
        repeat_password = self.cleaned_data.get("repeat_password")
        if not self.instance and not password:
            raise forms.ValidationError("Password is required")
        if self.instance and not password and not repeat_password:
            return
        if password != repeat_password:
            raise forms.ValidationError("Passwords do not match")
        return repeat_password

    def clean_home_bets(self):
        home_bet_ids = self.cleaned_data.get("home_bets")
        if not home_bet_ids:
            raise forms.ValidationError("Home bets are required")
        return [int(h) for h in home_bet_ids]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.fields["username"].disabled = True
            self.fields["username"].initial = instance.user.username
            self.fields["email"].initial = instance.user.email
            self.fields["first_name"].initial = instance.user.first_name
            self.fields["last_name"].initial = instance.user.last_name
            self.fields["home_bets"].disabled = True
            self.fields["home_bets"].initial = [
                b.home_bet_id for b in instance.balances.all()
            ]

    def save_m2m(self):
        pass

    def save(self, commit=False):
        home_bet_ids = self.cleaned_data.pop("home_bets")
        username = self.cleaned_data.pop("username")
        email = self.cleaned_data.pop("email")
        phone_number = self.cleaned_data.pop("phone_number")
        password = self.cleaned_data.pop("password")
        first_name = self.cleaned_data.pop("first_name", None)
        last_name = self.cleaned_data.pop("last_name", None)
        if not self.instance:
            instance = services.create_customer(
                username=username,
                email=email,
                phone_number=phone_number,
                password=password,
                home_bet_ids=home_bet_ids,
                first_name=first_name,
                last_name=last_name,
            )
            return instance
        instance = services.update_customer(
            customer_id=self.instance.id,
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )
        return instance


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAddForm
    list_display = ["username", "email", "phone_number", "home_bets"]

    @admin.display(description="Email")
    def username(self, obj):
        return obj.user.username

    @admin.display(description="Email")
    def email(self, obj):
        return obj.user.email

    @admin.display(description="First name")
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(description="Last name")
    def last_name(self, obj):
        return obj.user.last_name

    @admin.display(description="Home bets")
    def home_bets(self, obj):
        return ", ".join(obj.balances.values_list("home_bet__name", flat=True))

    # def has_change_permission(self, request, obj=None):
    #    return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CustomerBalance)
class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ["customer", "home_bet", "amount"]


@admin.register(CustomerPlan)
class CustomerPlanAdmin(admin.ModelAdmin):
    class CustomerPlanForm(forms.ModelForm):
        class Meta:
            model = CustomerPlan
            fields = ["customer", "plan", "start_dt", "end_dt", "is_active"]

        def clean_customer(self):
            customer = self.cleaned_data.get("customer")
            if not self.instance.pk:
                active_plans = selectors.filter_customer_plans(
                    customer_id=customer.id, is_active=True
                ).exists()
                if active_plans:
                    raise forms.ValidationError(
                        "Customer already has an active plan"
                    )
            return customer

        def save_m2m(self):
            pass

        def save(self, commit=True):
            if not self.instance.pk:
                plan = self.cleaned_data["plan"]
                start_dt = datetime.now().date()
                end_dt = start_dt + timedelta(days=plan.duration_in_days)
                self.instance.start_dt = start_dt
                self.instance.end_dt = end_dt
            instance = super().save(commit=True)

            customer = instance.customer
            user = customer.user
            if instance.is_active:
                user.is_active = True
                user.save()
            else:
                active_plans = selectors.filter_customer_plans(
                    customer_id=customer.id, is_active=True
                ).exists()
                if not active_plans:
                    user.is_active = False
                    user.save()
            return instance

    form = CustomerPlanForm
    list_display = ["customer", "plan", "start_dt", "end_dt", "is_active"]
    list_filter = ["is_active", "plan__name"]
    fields = ["customer", "plan", "start_dt", "end_dt", "is_active"]

    def get_readonly_fields(self, request, obj=None):
        return ["customer", "plan"] if obj else ["start_dt", "end_dt"]
