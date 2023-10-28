# Django
from django.contrib.auth import login
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer

# Libraries
from knox.views import LoginView as KnoxLoginView

# Internal
from apps.django_projects.auth import services
from apps.django_projects.auth.serializers import AuthSerializer


class LoginView(KnoxLoginView):
    serializer_class = AuthSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        response = super(LoginView, self).post(request, format=None)
        token = response.data.get("token")
        if token:
            services.delete_other_tokens(request=request, new_token=token)
        return response


class VerifyView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return HttpResponse(status=200)
