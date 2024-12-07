from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from clients.models import Client
from employees.models import Employee


class Attendance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="attendances")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)  # Příznak uzavřeného záznamu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def clean(self):
        if self.check_out_time and self.check_in_time and self.check_out_time < self.check_in_time:
            raise ValidationError("Čas odchodu nemůže být dříve než čas příchodu.")
        if self.is_closed and not self.check_out_time:
            raise ValidationError("Uzavřený záznam musí mít vyplněný čas odchodu.")
        if self.is_closed and not self.check_in_time:
            raise ValidationError("Uzavřený záznam musí mít vyplněný čas příchodu.")
        # if self.is_closed and not self.attendancetask_set.exists():
        #     raise ValidationError("Uzavřený záznam musí mít alespoň jeden úkon.")
        # if self.is_closed and self.attendancetask_set.filter(task__is_active=False).exists():
        #     raise ValidationError("Uzavřený záznam nemůže obsahovat neaktivní úkony.")
        if self.is_closed and self.check_out_time and self.check_in_time:
            if self.total_duration() > (self.check_out_time - self.check_in_time).seconds // 60:
                raise ValidationError("Celkový čas úkonů je delší než čas mezi příchodem a odchodem.")
        
