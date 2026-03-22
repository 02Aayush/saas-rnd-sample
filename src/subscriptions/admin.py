from django.contrib import admin

# Register your models here.
from .models import Subscription, UserSubscription

# used to register the subscription model in the admin site
admin.site.register(Subscription)
admin.site.register(UserSubscription)