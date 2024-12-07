import qrcode
from io import BytesIO
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.shortcuts import get_object_or_404
from .models import Client
import os
import environ

# Registrace fontu podporujícího diakritiku
FONT_PATH = os.path.join(os.path.dirname(__file__), 'static/fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))

env = environ.Env()

def generate_qr_image(data):
    """
    Vytvoří QR kód a vrátí ho jako ImageReader objekt.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return ImageReader(buffer)

def generate_qr_pdf(client_id):
    """
    Vytvoří PDF obsahující QR kódy pro checkin a checkout daného klienta.
    """
    client = get_object_or_404(Client, id=client_id)
    client_name = f"{client.first_name} {client.last_name}"

    # URL pro QR kódy
    base_url = settings.BASE_URL
    checkin_url = f"{base_url}/checkin/{client_id}"
    checkout_url = f"{base_url}/checkout/{client_id}"

    # Vytvoření QR kódů
    checkin_qr = generate_qr_image(checkin_url)
    checkout_qr = generate_qr_image(checkout_url)

    # Vytvoření PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    c.setFont("DejaVu", 16)
    
    # Nadpis s ID a jménem klienta
    c.setFont("DejaVu", 18)
    c.drawCentredString(300, 770, f"QR kódy pro klienta ID {client_id}")
    c.setFont("DejaVu", 16)
    c.drawCentredString(300, 745, f"Jméno: {client_name}")

    # Check-in sekce
    c.setFont("DejaVu", 14)
    c.drawCentredString(300, 720, "Check-in")
    c.drawImage(checkin_qr, 225, 565, width=150, height=150)
    c.setFont("DejaVu", 12)
    c.drawCentredString(300, 550, f"URL: {checkin_url}")

    # Oddělení sekcí
    c.line(50, 520, 550, 520)  # Vodorovná čára pro vizuální oddělení

    # Check-out sekce
    c.setFont("DejaVu", 14)
    c.drawCentredString(300, 480, "Check-out")
    c.drawImage(checkout_qr, 225, 325, width=150, height=150)
    c.setFont("DejaVu", 12)
    c.drawCentredString(300, 310, f"URL: {checkout_url}")

    # Dokončení PDF
    c.save()
    buffer.seek(0)
    return buffer


def qr_pdf_view(request, client_id):
    """
    Endpoint pro generování PDF s QR kódy.
    """
    pdf_buffer = generate_qr_pdf(client_id)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"qr_codes_client_{client_id}.pdf")
