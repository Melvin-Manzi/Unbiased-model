from rest_framework import serializers
from .models import StudentPerformance


class StudentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:                               # ← indented under the outer class
        model = StudentPerformance            # ← indented under Meta
        fields = '__all__'                    # ← indented under Meta + quoted string