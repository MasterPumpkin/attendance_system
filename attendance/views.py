from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.conf import settings
from io import BytesIO
from .utils import generate_qr_code, generate_qr_image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from attendance.models import Client
import qrcode
import os
import environ

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance, Employee, Client
from django.utils.timezone import now

# Registrace fontu podporujícího diakritiku
FONT_PATH = os.path.join(os.path.dirname(__file__), 'static/fonts', 'DejaVuSans.ttf')
pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))

env = environ.Env()

class RecordAttendanceView(APIView):
    def post(self, request):
        try:
            # Přijatá data
            data = request.data
            employee_id = data.get('employee_id')
            client_id = data.get('client_id')
            record_type = data.get('type')  # 'checkin' nebo 'checkout'

            # Validace dat
            if not all([employee_id, client_id, record_type]):
                return Response({'error': 'Chybí povinná data!'}, status=status.HTTP_400_BAD_REQUEST)

            # Načtení zaměstnance a klienta
            employee = Employee.objects.get(id=employee_id)
            client = Client.objects.get(id=client_id)

            # Načtení posledního záznamu (pokud existuje)
            last_attendance = Attendance.objects.filter(employee=employee, client=client).order_by('-created_at').first()

            if record_type == 'checkin':
                # Případ 1: Neexistuje žádný záznam -> vytvoříme nový
                if not last_attendance:
                    attendance = Attendance.objects.create(
                        employee=employee,
                        client=client,
                        check_in_time=now(),
                    )
                    return Response({'status': 'success', 'message': 'Check-in vytvořen.'}, status=status.HTTP_201_CREATED)

                # Případ 2: Existuje poslední záznam bez check-out -> ignorujeme
                if not last_attendance.is_closed:
                    return Response({'status': 'ignored', 'message': 'Poslední check-in není uzavřen, nový nebyl vytvořen.'}, status=status.HTTP_200_OK)

                # Případ 3: Vytvoříme nový záznam
                attendance = Attendance.objects.create(
                    employee=employee,
                    client=client,
                    check_in_time=now(),
                )
                return Response({'status': 'success', 'message': 'Check-in vytvořen.'}, status=status.HTTP_201_CREATED)

            elif record_type == 'checkout':
                # Případ 4: Neexistuje záznam s check-in -> ignorujeme
                if not last_attendance or last_attendance.is_closed:
                    return Response({'status': 'ignored', 'message': 'Neexistuje otevřený záznam pro check-out.'}, status=status.HTTP_200_OK)

                # Případ 5: Existuje záznam s check-in -> doplníme check-out
                last_attendance.check_out_time = now()
                last_attendance.is_closed = True  # Uzavření záznamu
                last_attendance.save()
                return Response({'status': 'success', 'message': 'Check-out zapsán.'}, status=status.HTTP_200_OK)

            # Neplatný typ akce
            return Response({'error': 'Neplatný typ akce!'}, status=status.HTTP_400_BAD_REQUEST)

        except Employee.DoesNotExist:
            return Response({'error': 'Zaměstnanec neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Client.DoesNotExist:
            return Response({'error': 'Klient neexistuje!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



def qr_scanner_view(request):
    return render(request,'attendance/scan.html')


def qr_code_view(request, action, client_id):
    data = f"{env('BASE_API_URL')}/{action}/{client_id}"
    img = generate_qr_code(data)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")


def qr_page_view(request, client_id):
    """
    Vygeneruje stránku s QR kódy pro checkin a checkout pro daného klienta.
    """
    base_url = env('BASE_API_URL')
    checkin_url = f"{base_url}/checkin/{client_id}"
    checkout_url = f"{base_url}/checkout/{client_id}"

    # Generování QR kódů
    checkin_qr = generate_qr_code(checkin_url)
    checkout_qr = generate_qr_code(checkout_url)

    context = {
        'client_id': client_id,
        'checkin_qr': checkin_qr,
        'checkout_qr': checkout_qr,
        'checkin_url': checkin_url,
        'checkout_url': checkout_url,
    }
    return render(request, 'attendance/qr_page.html', context)


def generate_qr_pdf(client_id):
    """
    Vytvoří PDF obsahující QR kódy pro checkin a checkout.
    """
    # Načtení jména klienta z databáze
    client = get_object_or_404(Client, id=client_id)
    client_full_name = f"{client.first_name} {client.last_name}"
    
    # URL pro checkin a checkout
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
    c.drawCentredString(300, 745, f"Jméno: {client_full_name}")

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
    Endpoint pro generování PDF s QR kódy pro daného klienta.
    """
    pdf_buffer = generate_qr_pdf(client_id)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"qr_codes_client_{client_id}.pdf")



"""
# Vytvoření PDF s jedním QR kódem

def generate_qr_pdf(action, client_id):
    # Vytvoření QR kódu
    data = f"https://0d17-109-81-91-120.ngrok-free.app/api/attendance/{action}/{client_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Vytvoření obrázku QR kódu do paměti
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Převod QR obrázku na ImageReader objekt
    qr_image = ImageReader(img_buffer)

    # Vytvoření PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(120, 800, f"QR kód pro {action} klienta {client_id}")
    c.drawImage(qr_image, 100, 580, width=200, height=200)
    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer

def qr_pdf_view(request, action, client_id):
    pdf_buffer = generate_qr_pdf(action, client_id)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"{action}_{client_id}_qr.pdf")

"""
