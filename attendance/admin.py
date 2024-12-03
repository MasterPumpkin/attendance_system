from django.contrib import admin
from .models import Employee, Client, Attendance

# Základní registrace modelů

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'employee_code', 'is_active')
    search_fields = ('last_name', 'email', 'employee_code')
    list_filter = ('is_active',)
    ordering = ('last_name',)
    inlines = [AttendanceInline]

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name','first_name', 'address', 'client_code', 'is_active', 'created_at')
    search_fields = ('last_name', 'first_name', 'contact_info')
    list_filter = ('is_active',)
    ordering = ('last_name', 'first_name')
    inlines = [AttendanceInline]
    
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'client', 'check_in_time', 'check_out_time', 'created_at')
    search_fields = ('employee__name', 'client__name')
    list_filter = ('check_in_time', 'check_out_time')
    ordering = ('-created_at',)


    
