from django.contrib import admin
from .models import Employee
from attendances.admin import AttendanceInline

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone_number', 'employee_code', 'is_active')
    search_fields = ('last_name', 'phone_number', 'employee_code')
    list_filter = ('is_active',)
    ordering = ('last_name',)
    inlines = [AttendanceInline]
