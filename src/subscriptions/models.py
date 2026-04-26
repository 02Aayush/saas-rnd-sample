import helpers.billing
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save # technically post_save is a singal, which is a way for Django to let us know when something happens (e.g. a model is saved). We can listen for that signal and run some code in response.
from django.conf import settings
from django.urls import reverse

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
    ''' 
    A subscription plan = Stripe Product 
    '''
    name = models.CharField(max_length=150)
    subtitle = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission,
        limit_choices_to={"content_type__app_label": "subscriptions",
                          "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]
                          })
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text='Ordering on Django Pricing Page') 
    featured = models.BooleanField(default=True, help_text='Featured on Django Pricing Page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(null=True, blank=True, help_text="Features for pricing, separated by new lines")
    
    def __str__(self): # This is just for better readability in the admin site
        return f"{self.name}"
    
    class Meta:
        ordering = ['order', 'featured', '-updated']
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def get_features_as_list(self):
        if not self.features:
            return []
        return [x.strip() for x in self.features.split("\n")]
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = helpers.billing.create_product(
            name=self.name,
            metadata={
                "subscription_plan_id": self.id,
            }, raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        

class SubscriptionPrice(models.Model):
    ''' 
    subscription Price = Stripe Product 
    '''
    class Interval(models.TextChoices):
        MONTHLY = "month", "Month"
        YEARLY = "year", "Year"
        
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120, default=Interval.MONTHLY,
                                choices=Interval.choices
                                )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text='Ordering on Django Pricing Page') 
    featured = models.BooleanField(default=True, help_text='Featured on Django Pricing Page')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta: # meta means it's not a real model, it's just some metadata for the model.
        ordering = ['subscription__order', 'order', 'featured', '-updated']
    
    def get_checkout_url(self):
        return reverse("sub-price-checkout", kwargs={"price_id": self.id})
    
    @property
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_as_list()
    
    @property
    def display_sub_name(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.name
    
    @property
    def display_sub_subtitle(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.subtitle
    
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        """
        remove decimal places
        """
        return int(self.price * 100)
    
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    def save(self, *args, **kwargs):
        if (not self.stripe_id and
            self.product_stripe_id is not None):
            stripe_id = helpers.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={
                    "subscription_plan_price_id": self.id,
                },
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            # set all other prices for the same subscription to not featured
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval = self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)
    

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription,
                on_delete = models.SET_NULL, null=True, blank=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    original_period_start = models.DateTimeField(auto_now=False, 
                                                auto_now_add=False, blank=True, null=True)
    user_cancel = models.BooleanField(default=False)
    current_period_start = models.DateTimeField(auto_now=False, 
                                                auto_now_add=False, blank=True, null=True)
    current_period_end = models.DateTimeField(auto_now=False, 
                                                auto_now_add=False, blank=True, null=True)
    
    @property
    def billing_cycle_anchor(self):
        """
        https://docs.stripe.com/payments/checkout/billing-cycle
        billing_cycle_anchor is a timestamp that Stripe uses to determine when the billing cycle starts and ends.
        We can use the current_period_end as the billing_cycle_anchor, so that when the subscription renews,
        it will renew based on the current_period_end.
                
        """
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp())
    
    
    def save(self, *args, **kwargs):
        if (self.original_period_start is None and
            self.current_period_start is not None):
            self.original_period_start = self.current_period_start
             
        super().save(*args, **kwargs)

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