from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client
from attendances.admin import AttendanceInline

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone_number', 'address', 'is_active', 'qr_pdf_link')
    search_fields = ('last_name', 'first_name')
    list_filter = ('is_active',)
    ordering = ('last_name', 'first_name')
    inlines = [AttendanceInline]

    def qr_pdf_link(self, obj):
        """
        Generuje odkaz na PDF s QR kódy pro daného klienta.
        """
        url = reverse('clients:qr_pdf', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Stáhnout QR</a>', url)

    qr_pdf_link.short_description = 'QR kódy'

