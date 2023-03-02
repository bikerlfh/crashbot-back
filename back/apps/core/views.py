from rest_framework.views import APIView

from rest_framework import serializers, status
from rest_framework.response import Response

from apps.core import services
from apps.utils.django.mixin import APIErrorsMixin


class HomeBetMultiplierView(
    APIErrorsMixin,
    APIView,
):
    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        multipliers = serializers.ListSerializer(
            child=serializers.IntegerField()
        )

    def post(self, request):
        in_serializer = self.InputSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        services.save_multipliers(
            **in_serializer.validated_data
        )
        return Response(data={}, status=status.HTTP_201_CREATED)
