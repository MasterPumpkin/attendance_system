import qrcode
import base64
from io import BytesIO
from reportlab.lib.utils import ImageReader


def generate_qr_code(data):
    """
    Vytvoří QR kód a vrátí ho jako base64 string, který lze použít v HTML.
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

    # Převod QR kódu na base64 pro zobrazení v HTML
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64


def generate_qr_image(data):
    """
    Vytvoří QR kód a vrátí ho jako ImageReader objekt pro použití v reportlab.
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