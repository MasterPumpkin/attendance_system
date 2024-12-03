from django.urls import path
from . import views
from .views import RecordAttendanceView, qr_scanner_view, qr_code_view, qr_pdf_view, qr_page_view

app_name = 'attendance'

urlpatterns = [
    path('api/attendance/', RecordAttendanceView.as_view(), name='record_attendance'),
    path('scan/', qr_scanner_view, name='scan'),
    path('qr-code/<str:action>/<int:client_id>/', qr_code_view, name='qr_code'),
    # path('qr-pdf/<str:action>/<int:client_id>/', qr_pdf_view, name='qr_pdf'),
    path('qr-pdf/<int:client_id>/', qr_pdf_view, name='qr_pdf'),
    path('qr-page/<int:client_id>/', qr_page_view, name='qr_page'),
]