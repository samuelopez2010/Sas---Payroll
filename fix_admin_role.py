
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import User

def promote_first_user():
    print("Promoting first user to ADMIN...")
    # Get the first registered user or the one creating the company
    # Simplest heuristic: Get the user created most recently, or just all users who own a company?
    # Let's verify specifically the latest user as that's likely who is logged in testing.
    
    try:
        latest_user = User.objects.latest('date_joined')
        print(f"Found user: {latest_user.username} (Role: {latest_user.role})")
        
        if latest_user.role != 'ADMIN':
            latest_user.role = 'ADMIN'
            latest_user.save()
            print(f"User {latest_user.username} successfully promoted to ADMIN.")
        else:
            print(f"User {latest_user.username} is already an ADMIN.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    promote_first_user()
