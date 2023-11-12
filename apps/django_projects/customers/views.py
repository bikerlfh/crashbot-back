# Django
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.customers import services
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.rest.serializers import inline_serializer

# from apps.utils.django.views.cache import cache_on_request_data


class CustomerDataView(APIErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    class InputGETSerializer(serializers.Serializer):
        app_hash_str = serializers.CharField()

    class OutputGETSerializer(serializers.Serializer):
        customer_id = serializers.IntegerField()
        plan = inline_serializer(
            fields=dict(
                name=serializers.CharField(),
                with_ai=serializers.BooleanField(),
                start_dt=serializers.DateField(),
                end_dt=serializers.DateField(),
                is_active=serializers.BooleanField(),
                crash_app=inline_serializer(
                    fields=dict(
                        version=serializers.CharField(),
                        home_bet_game_id=serializers.IntegerField(),
                        home_bets=inline_serializer(
                            many=True,
                            fields=dict(
                                id=serializers.IntegerField(),
                                name=serializers.CharField(),
                                url=serializers.CharField(),
                                limits=serializers.JSONField(),
                            ),
                        ),
                    ),
                ),
            ),
            required=False,
            allow_null=True,
        )

    # @cache_on_request_data(cache_timeout=60 * 60 * 24)
    def get(self, request):
        user_id = request.user.id
        serializer = self.InputGETSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = services.get_customer_data(
            user_id=user_id, **serializer.validated_data
        )
        out_serializer = self.OutputGETSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.validated_data, status=status.HTTP_200_OK
        )


class CustomerBalanceView(APIErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    class InputGETSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()

    class OutputGETSerializer(serializers.Serializer):
        amount = serializers.FloatField()

    class InputPATCHSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        currency = serializers.CharField(
            max_length=5, allow_null=True, allow_blank=True
        )

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


class LiveCustomerView(APIErrorsMixin, APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        closing_session = serializers.BooleanField(
            required=False, default=False
        )
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        currency = serializers.CharField(
            max_length=5, allow_null=True, allow_blank=True
        )

    class OutputSerializer(serializers.Serializer):
        allowed_to_save_multiplier = serializers.BooleanField()

    def post(self, request):
        user = request.user
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = services.live_customer(
            customer_id=user.customer.id,
            **serializer.validated_data,
        )
        out_serializer = self.OutputSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(
            data=out_serializer.validated_data, status=status.HTTP_200_OK
        )
