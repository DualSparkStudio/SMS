from django.urls import path

from .views import DashboardAnalyticsView, LearningDashboardView

urlpatterns = [
    path('dashboard/', DashboardAnalyticsView.as_view(), name='dashboard_analytics'),
    path('learning/', LearningDashboardView.as_view(), name='learning_dashboard'),
]
