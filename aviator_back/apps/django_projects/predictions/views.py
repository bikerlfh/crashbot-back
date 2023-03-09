from rest_framework.views import APIView

from rest_framework import serializers, status
from rest_framework.response import Response

from apps.django_projects.predictions import services
from apps.utils.django.mixin import APIErrorsMixin


class PredictionView(
    APIErrorsMixin,
    APIView,
):
    class InputSerializer(serializers.Serializer):
        home_bet_id = serializers.IntegerField()
        multipliers = serializers.ListSerializer(
            child=serializers.DecimalField(
                max_digits=10,
                decimal_places=2
            ),
            required=False,
            allow_null=True
        )
        length_window = serializers.IntegerField(
            required=False
        )

    class OutputSerializer(serializers.Serializer):
        decision_tree = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=False
        )
        decision_tree_2 = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=False
        )
        linear_regression = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=False
        )
        sequential = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=False
        )
        sequential_2 = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=False
        )

    def post(self, request):
        in_serializer = self.InputSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        data = services.predict(
            **in_serializer.validated_data
        )
        out_serializer = self.OutputSerializer(
            data=data
        )
        out_serializer.is_valid(raise_exception=True)
        return Response(data=out_serializer.validated_data)
