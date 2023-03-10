# Django
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

# Internal
from apps.django_projects.predictions import services
from apps.utils.django.mixin import APIErrorsMixin
from apps.utils.rest.serializers import inline_serializer


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
        length_window = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        predictions = inline_serializer(
            fields=dict(
                model=serializers.CharField(),
                average_predictions=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
                prediction_value=serializers.DecimalField(
                    max_digits=5, decimal_places=2
                ),
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
