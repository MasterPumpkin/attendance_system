from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from clients.models import Client
from employees.models import Employee
import pytz


class Attendance(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='attendances')
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='attendances')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)  # Označení chybného záznamu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.check_out_time and self.check_in_time and self.check_out_time < self.check_in_time:
            raise ValidationError("Čas odchodu nemůže být dříve než čas příchodu.")
        if self.is_closed and not self.check_out_time:
            raise ValidationError("Uzavřený záznam musí mít vyplněný čas odchodu.")
        if self.is_closed and not self.check_in_time:
            raise ValidationError("Uzavřený záznam musí mít vyplněný čas příchodu.")
        if self.is_closed and self.check_out_time and self.check_in_time:
            if (self.check_out_time - self.check_in_time).seconds // 60 < 0:
                raise ValidationError("Časový rozdíl mezi příchodem a odchodem je neplatný.")


    def __str__(self):
        return f"{self.employee} - {self.client} ({self.check_in_time} - {self.check_out_time}) - ({'Uzavřeno' if self.is_closed else 'Otevřeno'})"

    def total_duration(self):
        """
        Vrací celkový čas strávený na všech úkonech.
        """
        return self.attendancetask_set.aggregate(total=Sum('task__duration_minutes'))['total'] or 0

    def total_points(self):
        """
        Vrací celkový počet bodů za všechny úkony.
        """
        return self.attendancetask_set.aggregate(total=Sum('task__points'))['total'] or 0
