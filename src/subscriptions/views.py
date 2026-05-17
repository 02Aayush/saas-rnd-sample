import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from subscriptions.models import SubscriptionPrice, UserSubscription

@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        print("Refresh Subscription")
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id, raw=False)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Your subscription has been refreshed.")
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_details_view.html', {"subscription": user_sub_obj})

@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(user_sub_obj.stripe_id,
                                                           reason="User requested cancellation",
                                                           feedback="other",
                                                           cancel_at_period_end=True,
                                                           raw=False)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Your subscription has been cancelled.")
        return redirect(user_sub_obj.get_absolute_url())
    
    return render(request, 'subscriptions/user_cancel_view.html', {"subscription": user_sub_obj})

# Create your views here.
def subscription_price_view(request, interval="month"):
    qs = SubscriptionPrice.objects.filter(featured=True)
    int_mo = SubscriptionPrice.Interval.MONTHLY
    int_yr = SubscriptionPrice.Interval.YEARLY
    object_list = qs.filter(interval=int_mo)
    url_path_name = "pricing_interval"
    mo_url = reverse(url_path_name, kwargs={"interval": int_mo})
    yr_url = reverse(url_path_name, kwargs={"interval": int_yr})
    active = int_mo
    if interval == int_yr:
        object_list = qs.filter(interval=int_yr)
        active = int_yr
    return render(request, "subscriptions/pricing.html", {
        "object_list": object_list,
        "mo_url": mo_url,
        "yr_url": yr_url,
        "active": active,
    })
