from django.contrib import admin
from .models import DiagnosisRecord


@admin.register(DiagnosisRecord)
class DiagnosisRecordAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'user', 'diagnosis', 'urgency', 'confidence', 'created_at']
    list_filter = ['urgency', 'created_at']
    search_fields = ['patient_id', 'diagnosis', 'user__username']
