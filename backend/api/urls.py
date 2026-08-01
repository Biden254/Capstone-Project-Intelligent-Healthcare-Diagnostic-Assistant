from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),

    # Reference data
    path('health/', views.HealthView.as_view(), name='health'),
    path('symptoms/', views.SymptomsView.as_view(), name='symptoms'),
    path('samples/', views.SamplesView.as_view(), name='samples'),

    # Core feature
    path('diagnose/', views.DiagnoseView.as_view(), name='diagnose'),
    path('history/', views.HistoryView.as_view(), name='history'),
]
