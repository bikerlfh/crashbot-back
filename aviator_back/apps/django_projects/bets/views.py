from rest_framework import serializers, status
from apps.django_projects.bets import services
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.utils.django.mixin import APIErrorsMixin


class CustomerBalanceView(
    APIErrorsMixin,
    APIView
):
    class InputGETSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            allow_null=True
        )

    class OutputGETSerializer(serializers.Serializer):
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )
        username = serializers.CharField()
        password = serializers.CharField()

    def get(self, request):
        serializer = self.InputGETSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = services.get_customer_balance_data(**serializer.validated_data)
        out_serializer = self.OutputGETSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            **out_serializer.validated_data,
            status=status.HTTP_200_OK
        )


class BetView(
    APIErrorsMixin,
    APIView
):
    class InputPostSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        username = serializers.CharField(required=False)
        password = serializers.CharField(required=False)

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
        out_serializer = self.OutputPostSerializer(data=bet)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.validated_data,
            status=status.HTTP_201_CREATED
        )

    def patch(self, request):
        serializer = self.InputPatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.process_bet(**serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
