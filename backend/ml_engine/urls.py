from django.urls import path

from .views import ModelComparisonView, ModelMetricsView, TrainModelsView

urlpatterns = [
    path('train/', TrainModelsView.as_view(), name='train_models'),
    path('comparison/', ModelComparisonView.as_view(), name='model_comparison'),
    path('metrics/', ModelMetricsView.as_view(), name='model_metrics'),
]
