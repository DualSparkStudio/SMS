from django.db import models


class Campaign(models.Model):
    """Detected spam/scam campaigns from clustered messages."""

    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    campaign_name = models.CharField(max_length=200)
    cluster_keywords = models.JSONField(default=list)
    sample_messages = models.JSONField(default=list)
    affected_users = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)
    risk_score = models.FloatField(default=0)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='medium')
    campaign_type = models.CharField(max_length=50, default='spam')
    detected_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-risk_score', '-detected_at']

    def __str__(self):
        return f'{self.campaign_name} (Risk: {self.risk_level})'
