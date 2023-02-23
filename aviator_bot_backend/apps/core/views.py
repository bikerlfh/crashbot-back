from rest_framework.views import APIView

from rest_framework import serializers, status
from rest_framework.response import Response

from apps.core import services
from apps.utils.rest.serializers import inline_serializer


class AddHomeBetResult(APIView):
    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        list_multipliers = serializers.ListSerializer(
            child=inline_serializer(
                fields=dict(
                    multiplier=serializers.DecimalField(
                        max_digits=8,
                        decimal_places=2
                    ),
                    number_of_players=serializers.IntegerField(
                        required=False
                    ),
                    multiplier_dt=serializers.DateTimeField(
                        required=False
                    )
                ),
            )
        )

    def post(self, request):
        in_serializer = self.InputSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        services.save_game_results(
            **in_serializer.validated_data
        )
        return Response(status=status.HTTP_200_OK)
