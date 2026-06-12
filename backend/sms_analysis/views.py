from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from campaigns.clustering import detect_campaigns, is_bulk_campaign_message
from ml_engine.hasadf import HASDFPipeline

from .models import Feedback, SMSMessage
from .serializers import FeedbackSerializer, SMSAnalyzeRequestSerializer, SMSMessageSerializer


class AnalyzeSMSView(APIView):
    """Analyze SMS using the Hybrid Adaptive Spam Detection Framework."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SMSAnalyzeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']

        pipeline = HASDFPipeline()
        result = pipeline.analyze(message)

        sms = SMSMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=message,
            prediction=result['prediction'],
            confidence=result['confidence'],
            language=result['language'],
            security_score=result['security_score'],
            fraud_type=result.get('fraud_type'),
            explanation=result['explanation'],
            phishing_analysis=result['phishing_analysis'],
            xai_data=result['xai_data'],
            suspicious_words=result['suspicious_words'],
            urls_found=result['urls_found'],
            hasadf_pipeline=result['pipeline_steps'],
        )

        if sms.prediction == 'spam' or is_bulk_campaign_message(message):
            detect_campaigns()

        return Response(SMSMessageSerializer(sms).data, status=status.HTTP_201_CREATED)


class SMSHistoryView(generics.ListAPIView):
    serializer_class = SMSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SMSMessage.objects.filter(user=self.request.user)


class SMSDetailView(generics.RetrieveAPIView):
    queryset = SMSMessage.objects.all()
    serializer_class = SMSMessageSerializer
    permission_classes = [permissions.AllowAny]


class SubmitFeedbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sms_id = request.data.get('sms_id')
        feedback_type = request.data.get('feedback')
        corrected_label = request.data.get('corrected_label')

        if not sms_id or feedback_type not in ('correct', 'wrong'):
            return Response(
                {'error': 'sms_id and feedback (correct/wrong) are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sms = SMSMessage.objects.get(pk=sms_id)
        except SMSMessage.DoesNotExist:
            return Response({'error': 'SMS not found.'}, status=status.HTTP_404_NOT_FOUND)

        feedback, _ = Feedback.objects.update_or_create(
            user=request.user,
            sms=sms,
            defaults={
                'feedback': feedback_type,
                'corrected_label': corrected_label if feedback_type == 'wrong' else None,
            },
        )
        return Response(FeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)
