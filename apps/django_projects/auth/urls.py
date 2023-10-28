# Django
from django.urls import path

# Libraries
from knox import views as knox_views

# Internal
from apps.django_projects.auth.views import (
    LoginView,
    VerifyView,
)

app_name = "core"

urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("verify/", VerifyView.as_view(), name="knox_verify"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(
        "logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"
    ),
]
