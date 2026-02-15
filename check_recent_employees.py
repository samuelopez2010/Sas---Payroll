
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from hr.models import Employee
from core.models import Company

def check_recent():
    print("Checking 5 most recent employees...")
    recent_employees = Employee.objects.all().order_by('-id')[:5]
    
    if not recent_employees:
        print("No employees found in DB.")
        return

    for emp in recent_employees:
        company_name = emp.company.name if emp.company else "None"
        print(f"ID: {emp.id} | Name: {emp.first_name} {emp.last_name} | Email: {emp.email} | Company: {company_name} (ID: {emp.company_id})")

    print("\n--- Companies ---")
    for c in Company.objects.all():
        print(f"ID: {c.id} | Name: {c.name}")

if __name__ == "__main__":
    check_recent()
