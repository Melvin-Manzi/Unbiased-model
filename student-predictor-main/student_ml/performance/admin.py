from django.contrib import admin

# Register your models here.

from .models import StudentPerformance, PredictionRecord


admin.site.register(StudentPerformance)


@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'predicted_performance_index',
        'hours_studied',
        'previous_scores',
        'sleep_hours',
        'sample_papers',
        'extracurricular',
    )
    list_filter = ('extracurricular',)
    ordering = ('-created_at',)
