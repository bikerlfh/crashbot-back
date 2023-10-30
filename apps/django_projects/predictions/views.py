# Django
from rest_framework import serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.customers.permissions import CanUserUseAI
from apps.django_projects.predictions import services
from apps.django_projects.predictions.constants import BotType, ModelStatus
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.django.views.cache import cache_on_request_data
from apps.utils.rest.serializers import inline_serializer
from apps.utils.tools import enum_to_choices


class PredictionView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated, CanUserUseAI]

    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        multipliers = serializers.ListSerializer(
            child=serializers.DecimalField(max_digits=10, decimal_places=2),
            required=False,
            allow_null=True,
        )
        model_home_bet_id = serializers.IntegerField(
            required=False,
            allow_null=True,
            default=None,
        )

    class OutputSerializer(serializers.Serializer):
        predictions = inline_serializer(
            fields=dict(
                id=serializers.IntegerField(),
                prediction=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                prediction_round=serializers.IntegerField(),
                probability=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                average_predictions=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                category_percentage=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
            ),
            many=True,
        )

    # @cache_on_request_data(cache_timeout=60 * 2)
    def post(self, request):
        in_serializer = self.InputSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        data = services.predict(**in_serializer.validated_data)
        out_serializer = self.OutputSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.validated_data)


class ModelHomeBetView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated, IsAdminUser]

    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        status = serializers.ChoiceField(
            choices=enum_to_choices(ModelStatus), required=False
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        home_bet_id = serializers.IntegerField()
        model_type = serializers.CharField()
        status = serializers.CharField()
        seq_len = serializers.IntegerField()
        average_predictions = serializers.DecimalField(
            max_digits=5, decimal_places=2
        )
        average_bets = serializers.DecimalField(max_digits=5, decimal_places=2)
        result_date = serializers.DateTimeField(
            required=False, allow_null=True
        )
        others = serializers.JSONField(required=False, allow_null=True)
        category_results = inline_serializer(
            fields=dict(
                category=serializers.IntegerField(),
                correct_predictions=serializers.IntegerField(),
                incorrect_predictions=serializers.IntegerField(),
                percentage_predictions=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                correct_bets=serializers.IntegerField(),
                incorrect_bets=serializers.IntegerField(),
                percentage_bets=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                other_info=serializers.JSONField(
                    required=False,
                    allow_null=True,
                ),
            ),
            many=True,
        )

    def get(self, request):
        in_serializer = self.InputSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        data = services.get_models_home_bet(**in_serializer.validated_data)
        out_serializer = self.OutputSerializer(data=data, many=True)
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.validated_data)


class BotView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        bot_id = serializers.IntegerField(required=False, allow_null=True)
        bot_type = serializers.ChoiceField(
            choices=enum_to_choices(BotType), required=False
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        bot_type = serializers.CharField()
        number_of_min_bets_allowed_in_bank = serializers.IntegerField()
        risk_factor = serializers.FloatField()
        min_multiplier_to_bet = serializers.FloatField()
        min_multiplier_to_recover_losses = serializers.FloatField()
        min_probability_to_bet = serializers.FloatField()
        min_category_percentage_to_bet = serializers.FloatField()
        max_recovery_percentage_on_max_bet = serializers.FloatField()
        min_average_model_prediction = serializers.FloatField()
        stop_loss_percentage = serializers.FloatField()
        take_profit_percentage = serializers.FloatField()
        conditions = inline_serializer(
            fields=dict(
                id=serializers.IntegerField(),
                condition_on=serializers.CharField(),
                condition_on_value=serializers.FloatField(),
                condition_on_value_2=serializers.FloatField(
                    required=False, allow_null=True
                ),
                actions=serializers.JSONField(),
                others=serializers.JSONField(required=False, allow_null=True),
            ),
            many=True,
        )

    # @cache_on_request_data(cache_timeout=60 * 60 * 24 * 7)
    def get(self, request):
        in_serializer = self.InputSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        data = services.get_active_bots(**in_serializer.validated_data)
        out_serializer = self.OutputSerializer(data=data, many=True)
        out_serializer.is_valid(raise_exception=True)
        return Response(data=dict(bots=out_serializer.validated_data))


class EvaluateModelView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated, IsAdminUser]

    class InputSerializer(serializers.Serializer):
        model_home_bet_id = serializers.IntegerField()
        count_multipliers = serializers.IntegerField(
            required=False, allow_null=True
        )
        probability_to_eval = serializers.FloatField(
            required=False, allow_null=True
        )
        today_multipliers = serializers.BooleanField(
            required=False, allow_null=True
        )

    class OutputSerializer(serializers.Serializer):
        average_predictions = serializers.DecimalField(
            max_digits=5, decimal_places=2
        )
        category_results = inline_serializer(
            fields=dict(
                category=serializers.IntegerField(),
                correct_predictions=serializers.IntegerField(),
                incorrect_predictions=serializers.IntegerField(),
                percentage_predictions=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                correct_bets=serializers.IntegerField(),
                incorrect_bets=serializers.IntegerField(),
                percentage_bets=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
            ),
            many=True,
        )

    def get(self, request):
        in_serializer = self.InputSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        data = services.evaluate_model(**in_serializer.validated_data)
        out_serializer = self.OutputSerializer(data=data)
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.validated_data)


class GetPositionValuesView(
    APIErrorsMixin,
    APIView,
):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        home_bet_game_id = serializers.IntegerField()

    @cache_on_request_data(cache_timeout=60 * 15)
    def get(self, request):
        in_serializer = self.InputSerializer(data=request.GET)
        in_serializer.is_valid(raise_exception=True)
        data = services.get_position_values(**in_serializer.validated_data)
        return Response(data=data)
