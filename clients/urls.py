from django.urls import path
from .views import qr_pdf_view

app_name = 'clients'

urlpatterns = [
    path('qr-pdf/<int:client_id>/', qr_pdf_view, name='qr_pdf'),
]
