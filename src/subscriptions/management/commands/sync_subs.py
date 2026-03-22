from typing import Any
from django.core.management.base import BaseCommand
from subscriptions.models import subscription

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        print("Syncing subscriptions...")
        qs = subscription.objects.filter(active=True)
        
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
            