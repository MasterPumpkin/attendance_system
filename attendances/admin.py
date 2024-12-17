from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.contrib import admin
from django.db.models import QuerySet
from .models import Attendance
from catalogs.models import AttendanceTask
from catalogs.forms import ActiveCatalogForm


class AttendanceTaskInline(admin.TabularInline):
    model = AttendanceTask
    # fields = ('task', 'note')
    form = ActiveCatalogForm
    extra = 1

@admin.action(description="Označit vybrané záznamy jako uzavřené")
def mark_as_closed(modeladmin, request, queryset: QuerySet):
    no_tasks = queryset.filter(is_closed=False).exclude(id__in=AttendanceTask.objects.values_list('attendance_id', flat=True))
    with_tasks = queryset.filter(is_closed=False, id__in=AttendanceTask.objects.values_list('attendance_id', flat=True))

    if no_tasks.exists():
        modeladmin.message_user(
            request,
            f"{no_tasks.count()} záznam(y) nelze uzavřít, protože nemají žádné úkony.",
            level="error"
        )

    updated_count = with_tasks.update(is_closed=True)
    if updated_count > 0:
        modeladmin.message_user(
            request,
            f"{updated_count} záznam(y) byly úspěšně označeny jako uzavřené.",
            level="success"
        )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'employee', 
        'client', 
        'check_in_time', 
        'check_out_time', 
        'is_closed', 
        'is_error', 
        'close_record_action',
    )
    search_fields = ('employee__last_name', 'client__last_name')
    list_filter = ('is_closed', 'is_error')
    ordering = ('-created_at',)
    actions = [mark_as_closed]  # Registrace nové akce
    inlines = [AttendanceTaskInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/close/',
                self.admin_site.admin_view(self.close_record_view),
                name='close_attendance_record',
            ),
        ]
        return custom_urls + urls

    def close_record_view(self, request, pk):
        """Zavře záznam, pokud má přidružené AttendanceTask, jinak vrátí zprávu."""
        attendance = get_object_or_404(Attendance, pk=pk)
        if not AttendanceTask.objects.filter(attendance=attendance).exists():
            self.message_user(request, f"Záznam {attendance} nelze uzavřít, protože nemá žádné úkony.", level="error")
        else:
            attendance.is_closed = True
            attendance.save()
            self.message_user(request, f"Záznam pro klienta {attendance.client} a zaměstnance {attendance.employee} byl uzavřen.")
        return redirect(request.META.get('HTTP_REFERER', '/admin/attendances/attendance/'))

    def close_record_action(self, obj):
        """Zobrazí stav a možnosti akce ve sloupci."""
        if obj.is_closed:
            return "Uzavřeno"
        elif not AttendanceTask.objects.filter(attendance=obj).exists():
            # Červený text pro otevřené záznamy bez úkolů
            return format_html('<span style="color: red;">Otevřeno</span>')
        else:
            # Tlačítko pro zavření záznamu
            url = reverse('admin:close_attendance_record', args=[obj.pk])
            return format_html(f'<a class="button" href="{url}">Zavřít</a>')

    close_record_action.short_description = 'Akce'
    close_record_action.allow_tags = True

    def total_duration(self, obj):
        return obj.total_duration()

    total_duration.short_description = 'Celkový čas (minuty)'

    def total_points(self, obj):
        return obj.total_points()

    total_points.short_description = 'Celkové body'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # return qs.filter(is_error=True)  # Zobrazení pouze chybných záznamů
        return qs
    
    get_queryset.short_description = 'Chybné záznamy'

# admin.site.register(Attendance, AttendanceAdmin)

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1  # Počet prázdných řádků pro nový záznam
    fields = ('employee', 'check_in_time', 'check_out_time')  # Zobrazovaná pole
    readonly_fields = ('check_in_time', 'check_out_time')  # Pole, která nelze editovat

