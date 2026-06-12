from django.urls import path

from .views import AnalyzeSMSView, SMSDetailView, SMSHistoryView, SubmitFeedbackView

urlpatterns = [
    path('analyze/', AnalyzeSMSView.as_view(), name='analyze_sms'),
    path('history/', SMSHistoryView.as_view(), name='sms_history'),
    path('<int:pk>/', SMSDetailView.as_view(), name='sms_detail'),
    path('feedback/', SubmitFeedbackView.as_view(), name='submit_feedback'),
]
