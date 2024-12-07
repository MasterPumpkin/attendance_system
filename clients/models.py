from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    client_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Signal pro automatické vyplnění client_code
@receiver(post_save, sender=Client)
def set_client_code(sender, instance, created, **kwargs):
    if created and not instance.client_code:
        instance.client_code = f"CLI-{instance.id}"
        instance.save()