import helpers.billing

from django.db.models import Q
from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription, SubscriptionStatus

def refresh_active_user_subscriptions(user_ids=None):
    active_qs_lookup = (
        Q(status=SubscriptionStatus.ACTIVE) |
        Q(status=SubscriptionStatus.TRAILING) # spelling mistake in trailing instead of trialing in models
    )
    qs = UserSubscription.objects.filter(active_qs_lookup)
    if isinstance(user_ids, list):
        qs = qs.filter(user_id__in=user_ids)
    elif isinstance(user_ids, int):
        qs = qs.filter(user_id__in=[user_ids])
    elif isinstance(user_ids, str):
        qs = qs.filter(user_id__in=[user_ids])
        
    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if obj.stripe_id:
            sub_data = helpers.billing.get_subscription(obj.stripe_id, raw=False)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            obj.save()
            complete_count += 1
    return complete_count == qs_count
 
def clear_dangling_subscriptions():
    qs = Customer.objects.filter(stripe_id__isnull=False)
    for customer_obj in qs:
        user = customer_obj.user
        customer_stripe_id = customer_obj.stripe_id
        print(f"Sync {user} - {customer_stripe_id} subs and remove old subs...")
        subs = helpers.billing.get_customer_active_subscription(customer_stripe_id)
        for sub in subs:
            existing_user_sub_qs = UserSubscription.objects.filter(stripe_id__iexact=f"{sub.id}".strip())
            if existing_user_sub_qs.exists():
                continue
            helpers.billing.cancel_subscription(sub.id, reason="Dangling active subscription", cancel_at_period_end=False)  
            # print(sub.id, existing_user_sub_qs.exists())
                
def sync_subs_groups_permissions():
    print("Syncing subscriptions...")
    qs = Subscription.objects.filter(active=True)
    
    if not qs.exists():
        print("No active subscriptions found.")
        return
    
    for obj in qs:
        groups = obj.groups.all()
        permissions = obj.permissions.all()
        
        if not groups.exists():
            print(f"'{obj.name}' has no groups assigned — skipping.")
            continue
            
        if not permissions.exists():
            print(f"'{obj.name}' has no permissions assigned — skipping.")
            continue
        sub_perms = obj.permissions.all()
        for group in groups:
            group.permissions.set(sub_perms) # set() is better than add() here to avoid duplicates and ensure exact sync
            # for perm in permissions:
            #     group.permissions.add(perm)
            # print(f"✅ Synced '{group.name}' with {permissions.count()} permission(s)")
    
    print("\nDone syncing subscriptions.")