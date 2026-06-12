from rest_framework import serializers

from .models import Feedback, SMSMessage


class SMSMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSMessage
        fields = '__all__'
        read_only_fields = (
            'id', 'prediction', 'confidence', 'language', 'security_score',
            'fraud_type', 'explanation', 'phishing_analysis', 'xai_data',
            'suspicious_words', 'urls_found', 'hasadf_pipeline', 'timestamp',
        )


class SMSAnalyzeRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=5000)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'sms', 'feedback', 'corrected_label', 'timestamp')
        read_only_fields = ('id', 'timestamp')
