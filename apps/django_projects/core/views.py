# Django
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.core import services
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.django.views.cache import cache_on_request_data


def health_check(request):
    return HttpResponse(status=200)


class HomeBetView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField()
        url = serializers.URLField()
        min_bet = serializers.DecimalField(max_digits=10, decimal_places=2)
        max_bet = serializers.DecimalField(max_digits=10, decimal_places=2)
        count_multipliers = serializers.IntegerField(default=0)
        currencies = serializers.ListSerializer(
            child=serializers.CharField(max_length=3)
        )

    @cache_on_request_data(cache_timeout=60 * 60 * 24 * 7)
    def get(self, request):
        in_serializer = self.InputSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        data = services.get_home_bet(
            home_bet_id=in_serializer.data.get("home_bet_id", None)
        )
        out_serializer = self.OutputSerializer(
            data=data, many=isinstance(data, list)
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.validated_data)


class HomeBetMultiplierView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated]

    class InputGetSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        count = serializers.IntegerField(required=False)

    class InputPostSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        multipliers = serializers.ListSerializer(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )

    class OutputSerializer(serializers.Serializer):
        multipliers = serializers.ListSerializer(
            child=serializers.FloatField()
        )

    def get(self, request):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        in_serializer = self.InputGetSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        multipliers = services.get_home_bet_multipliers(
            **in_serializer.validated_data
        )
        out_serializer = self.OutputSerializer(
            data=dict(multipliers=multipliers)
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.data)

    def post(self, request):
        in_serializer = self.InputPostSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        multipliers = services.save_multipliers(**in_serializer.validated_data)
        out_serializer = self.OutputSerializer(
            data=dict(multipliers=multipliers)
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.data, status=status.HTTP_201_CREATED
        )
