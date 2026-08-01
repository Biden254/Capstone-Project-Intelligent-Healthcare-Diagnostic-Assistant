from django.contrib.auth.models import User
from rest_framework import serializers

from .models import DiagnosisRecord


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )


class PatientInputSerializer(serializers.Serializer):
    patient_id     = serializers.CharField(required=False, allow_blank=True, default='')
    symptoms       = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    age            = serializers.IntegerField(min_value=0, max_value=120)
    temperature    = serializers.FloatField()
    heart_rate     = serializers.IntegerField(min_value=0)
    blood_pressure = serializers.CharField(max_length=20)


class DiagnosisRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisRecord
        fields = ['id', 'patient_id', 'symptoms', 'age', 'temperature', 'heart_rate',
                  'blood_pressure', 'diagnosis', 'confidence', 'urgency', 'report',
                  'treatment_plan', 'created_at']
