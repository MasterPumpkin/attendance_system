from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    employee_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    date_of_joining = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Client(models.Model):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    contact_info = models.JSONField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    client_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    check_in_qr_code = models.TextField()
    check_out_qr_code = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)  # Příznak uzavřeného záznamu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.client} ({'Uzavřeno' if self.is_closed else 'Otevřeno'})"

# Signal pro automatické vyplnění employee_code
@receiver(post_save, sender=Employee)
def set_employee_code(sender, instance, created, **kwargs):
    if created and not instance.employee_code:
        instance.employee_code = f"EMP-{instance.id}"
        instance.save()

# Signal pro automatické vyplnění client_code
@receiver(post_save, sender=Client)
def set_client_code(sender, instance, created, **kwargs):
    if created and not instance.client_code:
        instance.client_code = f"CLI-{instance.id}"
        instance.save()