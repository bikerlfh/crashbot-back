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

    class InputGETSerializer(serializers.Serializer):
        bet_id = serializers.IntegerField()

    class OutputGETSerializer(serializers.Serializer):
        id = serializers.IntegerField(source="bet_id")
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
        multiplier_result = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            allow_null=True
        )
        profit_amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            allow_null=True
        )
        status = serializers.CharField()

    class InputPOSTSerializer(serializers.Serializer):
        external_id = serializers.CharField(max_length=50)
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

    class OutputPOSTSerializer(serializers.Serializer):
        bet_id: serializers.IntegerField(
            source="id"
        )

    class InputPATCHSerializer(serializers.Serializer):
        bet_id = serializers.IntegerField()
        multiplier = serializers.FloatField()

    def get(self, request):
        serializer = self.InputGETSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        bet_data = services.get_bet(**serializer.validated_data)
        output_serializer = self.OutputGETSerializer(data=bet_data)
        output_serializer.is_valid(raise_exception=True)
        return Response(
            data=output_serializer.validated_data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.InputPOSTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bet = services.create_bet(**serializer.validated_data)
        return Response(
            data={'bet_id': bet.id},
            status=status.HTTP_201_CREATED
        )

    def patch(self, request):
        serializer = self.InputPATCHSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.process_bet(**serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
