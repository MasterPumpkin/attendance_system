from django.db import models
from django.core.exceptions import ValidationError

class Catalog(models.Model):
    name = models.CharField(max_length=255)
    catalog_number = models.CharField(max_length=50, unique=True)
    points = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()  # Čas v minutách
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.catalog_number} - {self.name}"

    def formatted_duration(self):
        """
        Vrací čas ve formátu HH:MM.
        """
        hours, minutes = divmod(self.duration_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"
  

class AttendanceTask(models.Model):
    attendance = models.ForeignKey('attendances.Attendance', on_delete=models.CASCADE)
    task = models.ForeignKey(Catalog, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)

    def clean(self):
        if not self.task.is_active:
            raise ValidationError(f"Úkon {self.task.name} je neaktivní a nelze jej přiřadit.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.attendance} - {self.task.name}"