# Django
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Libraries
from apps.django_projects.bets import services
from apps.django_projects.bets.constants import BetType
from apps.utils import tools
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.rest.serializers import inline_serializer


class BetView(APIErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    class InputGETSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField(required=False)
        status = serializers.CharField(required=False)

    class OutputGETSerializer(serializers.Serializer):
        id = serializers.IntegerField(source="bet_id")
        home_bet_id = serializers.IntegerField()
        prediction = serializers.FloatField()
        amount = serializers.FloatField()
        multiplier = serializers.FloatField()
        multiplier_result = serializers.FloatField(allow_null=True)
        profit_amount = serializers.FloatField(allow_null=True)
        status = serializers.CharField()

    class InputPOSTSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        balance_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
        bets = inline_serializer(
            fields=dict(
                external_id=serializers.CharField(max_length=50),
                prediction=serializers.FloatField(),
                amount=serializers.FloatField(),
                multiplier=serializers.FloatField(),
                multiplier_result=serializers.FloatField(),
                bet_type=serializers.ChoiceField(
                    choices=tools.enum_to_choices(BetType),
                    allow_null=True,
                    allow_blank=True,
                ),
            ),
            many=True,
        )

    class OutputPOSTSerializer(serializers.Serializer):
        bet_id: serializers.IntegerField(source="id")

    def get(self, request):
        in_serializer = self.InputGETSerializer(data=request.query_params)
        in_serializer.is_valid(raise_exception=True)
        bet_data = services.get_my_bets(
            **in_serializer.validated_data, user_id=request.user.id
        )
        output_serializer = self.OutputGETSerializer(data=bet_data, many=True)
        output_serializer.is_valid(raise_exception=True)
        return Response(
            data=output_serializer.validated_data, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.InputPOSTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bets = services.create_bets(
            **serializer.validated_data, customer_id=request.user.customer.id
        )
        bet_ids = [bet.id for bet in bets]
        return Response(data={"bet_ids": bet_ids}, status=status.HTTP_201_CREATED)
