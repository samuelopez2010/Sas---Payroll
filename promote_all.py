
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import User

def promote_all_users():
    print("Promoting ALL users to ADMIN...")
    
    users = User.objects.all()
    count = 0
    for user in users:
        # We generally want to promote everyone so they can test
        user.role = 'ADMIN'
        user.save()
        print(f"Promoted {user.username}")
        count += 1
            
    print(f"Done. Promoted {count} users.")

if __name__ == "__main__":
    promote_all_users()
