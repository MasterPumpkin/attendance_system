from django.urls import path
from .views import RecordAttendanceView, qr_scanner_view

app_name = 'attendances'

urlpatterns = [
    path('record/', RecordAttendanceView.as_view(), name='record_attendance'),
    path('scan/', qr_scanner_view, name='scan'),
]
