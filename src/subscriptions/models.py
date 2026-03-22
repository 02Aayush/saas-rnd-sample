from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save # technically post_save is a singal, which is a way for Django to let us know when something happens (e.g. a model is saved). We can listen for that signal and run some code in response.
from django.conf import settings

User = settings.AUTH_USER_MODEL # "auth.User"

AllOW_CUSTOM_GROUPS = True 

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
    
    def __str__(self): # This is just for better readability in the admin site
        return f"{self.name} Subscription"
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        
# The Problem:
# Django's RenameModel operation is broken when the only change is letter casing (e.g. subscription → Subscription). Instead of renaming
# the model in its internal state, it silently deleted it — causing Django to think the model didn't exist and keep trying to recreate it with CreateModel.
# The Fix:
# Replaced the broken RenameModel operation in 0007 with an empty no-op migration (no operations at all). This works because Django's model comparison is
# case-insensitive at runtime — so it sees subscription in migration state and Subscription in models.py as the same thing and doesn't complain. No database
# changes were needed since PostgreSQL table names are lowercase anyway.
# One line summary: Django can't rename a model by case alone, so we just did nothing and let Django's case-insensitive matching handle it.


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription,
    on_delete = models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

def user_sub_post_save(sender, instance, created, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not AllOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True) # [1, 2, 3, 4, 5]
        subs_groups_set = set(subs_groups) # {1, 2, 3, 4, 5}
        # groups_ids = groups.values_list("id", flat=True) # [1, 2, 3]
        current_groups = user.groups.all().values_list("id", flat=True) # [1, 4]
        groups_ids_set = set(groups_ids) # {1, 2, 3}
        current_groups_set = set(current_groups) - subs_groups_set # {4}
        final_groups_ids = list(groups_ids_set.union(current_groups_set)) # [1, 2, 3, 4]
        user.groups.set(final_groups_ids)

post_save.connect(user_sub_post_save, sender=UserSubscription)

# how UserSubscription and user_sub_post_save are working in simple terms is: 
# 1. Whenever a UserSubscription instance is saved (e.g. when a user changes their subscription), the post_save signal is triggered.
# 2. The user_sub_post_save function is called with the instance of UserSubscription that was just saved.
# 3. Inside user_sub_post_save, we get the user and the subscription associated with that UserSubscription instance.
# 4. We then get the groups associated with that subscription and update the user's groups accordingly. If AllOW_CUSTOM_GROUPS is False,
# we simply set the user's groups to match the subscription's groups. If it's True, we allow the user to keep any custom groups they had
# while also adding the subscription's groups and removing any groups from other subscriptions.