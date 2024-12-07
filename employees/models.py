from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    employee_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Signal pro automatické vyplnění employee_code
@receiver(post_save, sender=Employee)
def set_employee_code(sender, instance, created, **kwargs):
    if created and not instance.employee_code:
        instance.employee_code = f"EMP-{instance.id}"
        instance.save()


