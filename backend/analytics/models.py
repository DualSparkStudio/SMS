from django.db import models


class ModelTrainingLog(models.Model):
    """Tracks model retraining history for learning dashboard."""

    trained_at = models.DateTimeField(auto_now_add=True)
    samples_count = models.IntegerField()
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    model_name = models.CharField(max_length=100)
    included_feedback = models.BooleanField(default=False)

    class Meta:
        db_table = 'model_training_logs'
        ordering = ['-trained_at']
