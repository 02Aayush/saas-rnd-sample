import helpers.billing
from typing import Any
from django.core.management.base import BaseCommand

from customers.models import Customer
from subscriptions import utils as subscription_utils

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-dangling", action="store_true", default=False)
    
    def handle(self, *args: Any, **options: Any):
        # python manage.py sync_user_subs --clear-dangling
        # print(options)
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing dangling not in use active subs in stripe")
            subscription_utils.clear_dangling_subscriptions()
        else:
            print("Sync active subs")
            done = subscription_utils.refresh_active_user_subscriptions(active_only=True, verbose=True)
            if done:
                print("Done")