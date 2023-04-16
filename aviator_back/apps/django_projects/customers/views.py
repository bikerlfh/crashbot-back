# Django
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Internal
from apps.django_projects.customers import services
from apps.utils.django.mixin import APIErrorsMixin


class CustomerBalanceView(APIErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    class InputGETSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()

    class OutputGETSerializer(serializers.Serializer):
        amount = serializers.FloatField()
        # username = serializers.CharField()
        # password = serializers.CharField()

    class InputPATCHSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get(self, request):
        user = request.user
        serializer = self.InputGETSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = services.get_customer_balance_data(
            customer_id=user.customer.id,
            home_bet_id=serializer.data.get("home_bet_id", None),
        )
        out_serializer = self.OutputGETSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.validated_data, status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = self.InputPATCHSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.update_customer_balance(**serializer.validated_data)
        return Response(status=status.HTTP_200_OK)
