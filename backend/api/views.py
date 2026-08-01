from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics

from ai_engine.modules.agent import PatientPercept
from ai_engine.modules.ml_classifier import MLDiagnosticClassifier

from .ai_bridge import get_system, get_status
from .models import DiagnosisRecord
from .serializers import RegisterSerializer, PatientInputSerializer, DiagnosisRecordSerializer


# ── Auth ─────────────────────────────────────────────────────

class RegisterView(APIView):
    """POST { username, email, password } -> creates a user, returns JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {"id": user.id, "username": user.username, "email": user.email},
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """GET -> the logged-in user's basic info. Requires a valid access token."""

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username, "email": u.email})


# ── Reference data (public, no auth needed) ─────────────────

class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", **get_status()})


class SymptomsView(APIView):
    """Symptom vocabulary, for building the intake form."""
    permission_classes = [AllowAny]

    def get(self, request):
        features = MLDiagnosticClassifier.SYMPTOM_FEATURES
        return Response([
            {"id": f, "label": f.replace('_', ' ').title()} for f in features
        ])


class SamplesView(APIView):
    """A handful of ready-made demo patients for quick testing."""
    permission_classes = [AllowAny]

    def get(self, request):
        demo_patients = [
            {"patient_id": "P001", "symptoms": ["fever", "cough", "fatigue", "loss of smell"],
             "age": 34, "temperature": 38.9, "heart_rate": 98, "blood_pressure": "120/80"},
            {"patient_id": "P002", "symptoms": ["chest pain", "shortness of breath", "sweating"],
             "age": 61, "temperature": 37.4, "heart_rate": 128, "blood_pressure": "160/100"},
            {"patient_id": "P003", "symptoms": ["fever", "rash", "joint pain", "headache"],
             "age": 22, "temperature": 39.6, "heart_rate": 110, "blood_pressure": "110/70"},
            {"patient_id": "P004",
             "symptoms": ["frequent urination", "excessive thirst", "blurred vision", "fatigue"],
             "age": 52, "temperature": 37.0, "heart_rate": 82, "blood_pressure": "130/85"},
            {"patient_id": "P005", "symptoms": ["cough", "fatigue", "headache", "body aches"],
             "age": 29, "temperature": 37.6, "heart_rate": 76, "blood_pressure": "118/76"},
        ]
        return Response(demo_patients)


# ── Core feature: diagnose (requires auth) ──────────────────

class DiagnoseView(APIView):
    """
    POST {
      "patient_id": "P001",       # optional
      "symptoms": ["fever", ...],
      "age": 34,
      "temperature": 38.9,
      "heart_rate": 98,
      "blood_pressure": "120/80"
    }
    Runs the patient through the full agent pipeline (Perceive -> Think -> Act),
    generates a treatment plan, saves it to the user's history, and returns it.
    """

    def post(self, request):
        serializer = PatientInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        agent, planner = get_system()

        percept = PatientPercept(
            patient_id=data.get('patient_id') or f"user-{request.user.id}",
            symptoms=data['symptoms'],
            age=data['age'],
            temperature=data['temperature'],
            heart_rate=data['heart_rate'],
            blood_pressure=data['blood_pressure'],
        )
        report = agent.run(percept)

        # Per-module breakdown, for transparency in the UI
        module_breakdown = {}
        if agent.memory.diagnosis_history:
            last_results = agent.memory.diagnosis_history[-1]
            for name, result in last_results.items():
                if isinstance(result, dict):
                    module_breakdown[name] = {
                        "diagnosis": result.get("diagnosis"),
                        "confidence": result.get("confidence"),
                        "summary": result.get("summary"),
                    }

        plan = planner.create_treatment_plan(report['diagnosis'], report['urgency'])

        record = DiagnosisRecord.objects.create(
            user=request.user,
            patient_id=percept.patient_id,
            symptoms=data['symptoms'],
            age=data['age'],
            temperature=data['temperature'],
            heart_rate=data['heart_rate'],
            blood_pressure=data['blood_pressure'],
            diagnosis=report['diagnosis'],
            confidence=report['confidence'],
            urgency=report['urgency'],
            report=report,
            treatment_plan=plan,
        )

        return Response({
            "record_id": record.id,
            "report": report,
            "module_breakdown": module_breakdown,
            "treatment_plan": plan,
        })


class HistoryView(generics.ListAPIView):
    """GET -> the logged-in user's past diagnoses, newest first."""
    serializer_class = DiagnosisRecordSerializer

    def get_queryset(self):
        return DiagnosisRecord.objects.filter(user=self.request.user)
