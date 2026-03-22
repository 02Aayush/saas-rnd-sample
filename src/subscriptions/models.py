from django.db import models
from django.contrib.auth.models import Group, Permission


SUBSCRIPTION_PERMISSIONS = [
            ("advanced", "Advanced Perm"), # Subscriptions.advance
            ("pro", "Pro Perm"), # Subscriptions.pro
            ("basic", " Basic Perm"), # Subscriptions.basic
            ("basic_ai", " Basic AI Perm"), # Subscriptions.basic_ai
        ]

# Create your models here.
class subscription(models.Model):
    name = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission,
        limit_choices_to={"content_type__app_label": "subscriptions",
                          "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                          })
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
