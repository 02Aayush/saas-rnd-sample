from django.contrib import admin

# Register your models here.
from .models import subscription

# used to register the subscription model in the admin site
admin.site.register(subscription)