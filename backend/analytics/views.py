from collections import Counter
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from sms_analysis.models import Feedback, SMSMessage

from .models import ModelTrainingLog


class DashboardAnalyticsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total = SMSMessage.objects.count()
        spam_count = SMSMessage.objects.filter(prediction='spam').count()
        ham_count = SMSMessage.objects.filter(prediction='ham').count()

        spam_vs_ham = {
            'labels': ['Spam', 'Ham'],
            'values': [spam_count, ham_count],
        }

        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily = (
            SMSMessage.objects.filter(timestamp__gte=thirty_days_ago)
            .annotate(date=TruncDate('timestamp'))
            .values('date', 'prediction')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        date_map = {}
        for row in daily:
            d = str(row['date'])
            if d not in date_map:
                date_map[d] = {'spam': 0, 'ham': 0}
            date_map[d][row['prediction']] = row['count']

        daily_detection = {
            'labels': list(date_map.keys()),
            'spam': [date_map[d]['spam'] for d in date_map],
            'ham': [date_map[d]['ham'] for d in date_map],
        }

        fraud_qs = SMSMessage.objects.exclude(fraud_type__isnull=True).exclude(fraud_type='')
        fraud_counter = Counter(fraud_qs.values_list('fraud_type', flat=True))
        fraud_categories = {
            'labels': list(fraud_counter.keys()),
            'values': list(fraud_counter.values()),
        }

        lang_counter = Counter(SMSMessage.objects.values_list('language', flat=True))
        lang_names = {'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi'}
        language_distribution = {
            'labels': [lang_names.get(k, k) for k in lang_counter.keys()],
            'values': list(lang_counter.values()),
        }

        feedback_trend = (
            Feedback.objects.filter(timestamp__gte=thirty_days_ago)
            .annotate(date=TruncDate('timestamp'))
            .values('date', 'feedback')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        fb_map = {}
        for row in feedback_trend:
            d = str(row['date'])
            if d not in fb_map:
                fb_map[d] = {'correct': 0, 'wrong': 0}
            fb_map[d][row['feedback']] = row['count']

        user_reports = {
            'labels': list(fb_map.keys()),
            'correct': [fb_map[d]['correct'] for d in fb_map],
            'wrong': [fb_map[d]['wrong'] for d in fb_map],
        }

        return Response({
            'total_analyzed': total,
            'spam_count': spam_count,
            'ham_count': ham_count,
            'spam_vs_ham': spam_vs_ham,
            'daily_detection': daily_detection,
            'fraud_categories': fraud_categories,
            'language_distribution': language_distribution,
            'user_reports': user_reports,
            'feedback_total': Feedback.objects.count(),
            'accuracy_feedback': self._feedback_accuracy(),
        })

    def _feedback_accuracy(self):
        total = Feedback.objects.count()
        if total == 0:
            return 100.0
        correct = Feedback.objects.filter(feedback='correct').count()
        return round(correct / total * 100, 1)


class LearningDashboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logs = ModelTrainingLog.objects.all()[:10]
        return Response({
            'training_history': [
                {
                    'trained_at': log.trained_at.isoformat(),
                    'samples': log.samples_count,
                    'accuracy': log.accuracy,
                    'f1_score': log.f1_score,
                    'model': log.model_name,
                }
                for log in logs
            ],
            'feedback_pending': Feedback.objects.filter(feedback='wrong').count(),
            'total_feedback': Feedback.objects.count(),
        })
