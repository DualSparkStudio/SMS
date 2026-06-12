from django.conf import settings
from django.db import models


class SMSMessage(models.Model):
    """Stores analyzed SMS messages and predictions."""

    PREDICTION_CHOICES = [
        ('spam', 'Spam'),
        ('ham', 'Ham'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_messages',
    )
    message = models.TextField()
    prediction = models.CharField(max_length=10, choices=PREDICTION_CHOICES)
    confidence = models.FloatField()
    language = models.CharField(max_length=20, default='en')
    security_score = models.IntegerField(default=50)
    fraud_type = models.CharField(max_length=50, blank=True, null=True)
    explanation = models.JSONField(default=dict, blank=True)
    phishing_analysis = models.JSONField(default=dict, blank=True)
    xai_data = models.JSONField(default=dict, blank=True)
    suspicious_words = models.JSONField(default=list, blank=True)
    urls_found = models.JSONField(default=list, blank=True)
    hasadf_pipeline = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sms_messages'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.prediction} ({self.confidence:.0%}) - {self.message[:50]}'


class Feedback(models.Model):
    """User feedback for continuous learning."""

    FEEDBACK_CHOICES = [
        ('correct', 'Correct Prediction'),
        ('wrong', 'Wrong Prediction'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    sms = models.ForeignKey(
        SMSMessage,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    feedback = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    corrected_label = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
        unique_together = ('user', 'sms')

    def __str__(self):
        return f'{self.user.email} - {self.feedback}'
