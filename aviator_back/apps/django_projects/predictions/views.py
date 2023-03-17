# Django
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.predictions import services
from apps.django_projects.predictions.constants import ModelStatus
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.rest.serializers import inline_serializer
from apps.utils.tools import enum_to_choices


class PredictionView(
    APIErrorsMixin,
    APIView,
):
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
                average_predictions=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                category_percentage=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                )
            ),
            many=True,
        )

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
