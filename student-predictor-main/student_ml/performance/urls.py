from django.urls import path
from .views import predict_performance, prediction_history

urlpatterns = [
    path('predict/', predict_performance),
    path('history/', prediction_history),
]