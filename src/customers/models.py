from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL # "auth.User"
# Create your models here.

class Customer(models.Model):
    # name = models.CharField(max_length=150)
    # email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} Customer"