from django.contrib import admin
from .models import Attendance
from catalogs.models import AttendanceTask
from catalogs.forms import ActiveCatalogForm


class AttendanceTaskInline(admin.TabularInline):
    model = AttendanceTask
    # fields = ('task', 'note')
    form = ActiveCatalogForm
    extra = 1

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'client', 'check_in_time', 'check_out_time', 'total_duration', 'total_points', 'is_closed')
    search_fields = ('employee__last_name', 'client__last_name')
    list_filter = ('check_in_time', 'check_out_time')
    ordering = ('-created_at',)
    inlines = [AttendanceTaskInline]

    def total_duration(self, obj):
        return obj.total_duration()

    total_duration.short_description = 'Celkový čas (minuty)'

    def total_points(self, obj):
        return obj.total_points()

    total_points.short_description = 'Celkové body'


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1  # Počet prázdných řádků pro nový záznam
    fields = ('employee', 'check_in_time', 'check_out_time')  # Zobrazovaná pole
    readonly_fields = ('check_in_time', 'check_out_time')  # Pole, která nelze editovat

