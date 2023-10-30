"""aviator_bot_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django
from django.contrib import admin
from django.urls import include, path
from apps.django_projects.core import views as core_views


urlpatterns = [
    path("", core_views.index, name="index"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.django_projects.core.urls")),
    path("api/auth/", include("apps.django_projects.auth.urls")),
    path("api/customers/", include("apps.django_projects.customers.urls")),
    path("api/bets/", include("apps.django_projects.bets.urls")),
    path("api/predictions/", include("apps.django_projects.predictions.urls")),
]
