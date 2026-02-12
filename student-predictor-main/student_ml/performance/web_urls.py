from django.urls import path
from .views import predict_ui

urlpatterns = [
    path('', predict_ui),
]
