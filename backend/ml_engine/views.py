from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .predictor import SMSPredictor
from .trainer import train_all_models


class TrainModelsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        include_feedback = request.data.get('include_feedback', False)
        result = train_all_models(include_feedback=include_feedback)
        return Response(result, status=status.HTTP_200_OK)


class ModelComparisonView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        metrics = SMSPredictor.get_metrics()
        if not metrics:
            metrics = train_all_models()
        return Response(metrics)


class ModelMetricsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(SMSPredictor.get_metrics())
