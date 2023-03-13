from rest_framework import serializers, status
from apps.django_projects.customers import services
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

    class OutputGETSerializer(serializers.Serializer):
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )
        # username = serializers.CharField()
        # password = serializers.CharField()

    def get(self, request):
        serializer = self.InputGETSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = services.get_customer_balance_data(**serializer.validated_data)
        out_serializer = self.OutputGETSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.validated_data,
            status=status.HTTP_200_OK
        )


class UpdateCustomerBalanceView(
    APIErrorsMixin,
    APIView
):
    class InputGETSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        amount = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )

    def patch(self, request):
        serializer = self.InputGETSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.update_customer_balance(**serializer.validated_data)
        return Response(
            status=status.HTTP_200_OK
        )
