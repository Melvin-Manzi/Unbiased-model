from django.db import models

class StudentPerformance(models.Model):
    hours_studied     = models.IntegerField()
    previous_scores   = models.IntegerField()
    extracurricular   = models.BooleanField()
    sleep_hours       = models.IntegerField()
    sample_papers     = models.IntegerField()
    performance_index = models.FloatField()

    def __str__(self):                  
        return f"Student ~ Index: {self.performance_index}"  


class PredictionRecord(models.Model):
    hours_studied = models.IntegerField()
    previous_scores = models.IntegerField()
    extracurricular = models.BooleanField()
    sleep_hours = models.IntegerField()
    sample_papers = models.IntegerField()

    predicted_performance_index = models.FloatField()
    advice = models.JSONField(default=list, blank=True)
    warnings = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction ~ {self.predicted_performance_index} ({self.created_at})"