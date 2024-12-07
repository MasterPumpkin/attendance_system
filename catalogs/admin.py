from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .utils import import_catalog_from_csv, export_catalog_to_csv
from .models import Catalog, AttendanceTask


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog_number', 'points', 'price', 'formatted_duration', 'is_active', 'colored_status')
    list_filter = ('is_active',)
    search_fields = ('name', 'catalog_number')
    actions = ['export_as_csv', 'export_active_as_csv']

    def export_active_as_csv(self, request, queryset):
        """
        Exportuje aktivní katalogové položky do CSV.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catalog_active.csv"'
        response.write(export_catalog_to_csv(active_only=True))
        return response

    export_active_as_csv.short_description = 'Export pouze aktivních do CSV'


    def export_as_csv(self, request, queryset):
        """
        Exportuje katalogové položky do CSV.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catalog.csv"'
        response.write(export_catalog_to_csv())
        return response

    export_as_csv.short_description = 'Export do CSV'


    def import_from_csv(self, request, queryset):
        """
        Importuje katalogové položky z CSV.
        """
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                self.message_user(request, 'Nahraný soubor chybí.', level='error')
                return redirect('.')

            result = import_catalog_from_csv(csv_file)
            self.message_user(request, f"Přidáno: {result['added']}, Aktualizováno: {result['updated']}.")
            if result['errors']:
                for error in result['errors']:
                    self.message_user(request, error, level='error')
            return redirect('.')

        return render(request, 'admin/import_csv.html', {'title': 'Import CSV'})

    import_from_csv.short_description = 'Import z CSV'


    def colored_status(self, obj):
        """
        Barevné zobrazení aktivního/neaktivního stavu.
        """
        color = 'green' if obj.is_active else 'red'
        return format_html('<span style="color: {};">{}</span>', color, 'Aktivní' if obj.is_active else 'Neaktivní')

    colored_status.short_description = 'Stav'

    def get_urls(self):
        """
        Přidání vlastní URL pro import CSV.
        """
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv_view), name='catalog_import_csv'),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        """
        Zobrazuje formulář pro import CSV a zpracovává nahraný soubor.
        """
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                self.message_user(request, 'Chybí CSV soubor.', level='error')
                return redirect('admin:catalog_import_csv')

            result = import_catalog_from_csv(csv_file)
            self.message_user(request, f"Přidáno: {result['added']}, Aktualizováno: {result['updated']}.")
            if result['errors']:
                for error in result['errors']:
                    self.message_user(request, error, level='error')
            return redirect('..')  # Vrátí uživatele zpět do seznamu katalogů

        return render(request, 'admin/import_csv.html', {
            'title': 'Import CSV',
        })

    def import_csv_button(self, request):
        """
        Přidává tlačítko na stránku seznamu katalogů.
        """
        return {
            'import_csv_url': reverse('admin:catalog_import_csv'),
        }

    import_csv_button.short_description = 'Import CSV'


@admin.register(AttendanceTask)
class AttendanceTaskAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'task', 'note')
    search_fields = ('attendance__id', 'task__name')