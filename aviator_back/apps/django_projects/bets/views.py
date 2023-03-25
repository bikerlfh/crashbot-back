# Django
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.bets import services
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.rest.serializers import inline_serializer


class BetView(APIErrorsMixin, APIView):
    class InputGETSerializer(serializers.Serializer):
        bet_id = serializers.IntegerField()

    class OutputGETSerializer(serializers.Serializer):
        id = serializers.IntegerField(source="bet_id")
        prediction = serializers.FloatField()
        prediction_round = serializers.IntegerField()
        amount = serializers.FloatField()
        multiplier = serializers.FloatField()
        multiplier_result = serializers.FloatField(allow_null=True)
        profit_amount = serializers.FloatField(allow_null=True)
        status = serializers.CharField()

    class InputPOSTSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        bets = inline_serializer(
            fields=dict(
                external_id=serializers.CharField(max_length=50),
                prediction=serializers.FloatField(),
                amount=serializers.FloatField(),
                multiplier=serializers.FloatField(),
                multiplier_result=serializers.FloatField()
            ),
            many=True,
        )

    class OutputPOSTSerializer(serializers.Serializer):
        bet_id: serializers.IntegerField(source="id")

    def get(self, request):
        serializer = self.InputGETSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        bet_data = services.get_bet(**serializer.validated_data)
        output_serializer = self.OutputGETSerializer(data=bet_data)
        output_serializer.is_valid(raise_exception=True)
        return Response(
            data=output_serializer.validated_data, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.InputPOSTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bets = services.create_bets(**serializer.validated_data)
        bet_ids = [bet.id for bet in bets]
        return Response(
            data={"bet_ids": bet_ids}, status=status.HTTP_201_CREATED
        )
