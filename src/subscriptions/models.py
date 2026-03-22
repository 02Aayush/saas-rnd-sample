from django.db import models
from django.contrib.auth.models import Group, Permission

SUBSCRIPTION_PERMISSIONS = [
            ("advanced", "Advanced Perm"), # Subscriptions.advance
            ("pro", "Pro Perm"), # Subscriptions.pro
            ("basic", " Basic Perm"), # Subscriptions.basic
            ("basic_ai", " Basic AI Perm"), # Subscriptions.basic_ai
        ]

# Create your models here.
class Subscription(models.Model):
    name = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission,
        limit_choices_to={"content_type__app_label": "subscriptions",
                          "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                          })
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        
# The Problem:
# Django's RenameModel operation is broken when the only change is letter casing (e.g. subscription → Subscription). Instead of renaming the model in its internal state, it silently deleted it — causing Django to think the model didn't exist and keep trying to recreate it with CreateModel.
# The Fix:
# Replaced the broken RenameModel operation in 0007 with an empty no-op migration (no operations at all). This works because Django's model comparison is case-insensitive at runtime — so it sees subscription in migration state and Subscription in models.py as the same thing and doesn't complain. No database changes were needed since PostgreSQL table names are lowercase anyway.
# One line summary: Django can't rename a model by case alone, so we just did nothing and let Django's case-insensitive matching handle it.

