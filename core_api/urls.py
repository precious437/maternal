from django.urls import path
from .views import VitalsView, FileUploadView, LoginView, HistoryView, SignupView

urlpatterns = [
    path('vitals/', VitalsView.as_view(), name='save-vitals'),
    path('upload/', FileUploadView.as_view(), name='upload-scan'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('history/', HistoryView.as_view(), name='api-history'),
]
