# Django
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.bets import services
from apps.utils.django.mixin import APIErrorsMixin


class BetView(
    APIErrorsMixin,
    APIView
):
    class InputPostSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        prediction = serializers.DecimalField(
            max_digits=5,
            decimal_places=2
        )
        prediction_round = serializers.IntegerField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        multiplier = serializers.DecimalField(
            max_digits=5,
            decimal_places=2
        )

    class OutputPostSerializer(serializers.Serializer):
        bet_id: serializers.IntegerField(
            source="id"
        )

    class InputPatchSerializer(serializers.Serializer):
        bet_id = serializers.IntegerField()
        multiplier = serializers.FloatField()

    def post(self, request):
        serializer = self.InputPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bet = services.create_bet(**serializer.validated_data)
        return Response(
            data={'bet_id': bet.id},
            status=status.HTTP_201_CREATED
        )

    def patch(self, request):
        serializer = self.InputPatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.process_bet(**serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
