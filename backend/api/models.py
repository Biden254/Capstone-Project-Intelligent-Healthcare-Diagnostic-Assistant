from django.db import models
from django.contrib.auth.models import User


class DiagnosisRecord(models.Model):
    """One run of the AI pipeline for one patient, tied to the user who ran it."""
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnoses')
    patient_id      = models.CharField(max_length=64, blank=True)
    symptoms        = models.JSONField(default=list)
    age             = models.PositiveIntegerField()
    temperature     = models.FloatField()
    heart_rate      = models.PositiveIntegerField()
    blood_pressure  = models.CharField(max_length=20)
    diagnosis       = models.CharField(max_length=128)
    confidence      = models.FloatField()
    urgency         = models.CharField(max_length=20)
    report          = models.JSONField()
    treatment_plan  = models.JSONField()
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_id or 'patient'} — {self.diagnosis} ({self.created_at:%Y-%m-%d %H:%M})"
