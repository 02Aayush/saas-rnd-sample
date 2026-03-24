import helpers.billing
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
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            email = self.user.email
            if email != "" or email is None:
                stripe_id = helpers.billing.create_customer(email=email, raw=False)
                self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        # post-save will not update
        # self.stripe_id = "Something else"
        # self.save()