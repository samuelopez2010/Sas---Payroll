
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from hr.models import Employee
from core.models import Company, User

def diagnose():
    with open('diagnosis_utf8.txt', 'w', encoding='utf-8') as f:
        f.write("=== USERS ===\n")
        for u in User.objects.all():
            f.write(f"User: {u.username} | Role: {u.role} | Company: {u.company.name if u.company else 'None'} (ID: {u.company_id})\n")

        f.write("\n=== COMPANIES ===\n")
        for c in Company.objects.all():
            f.write(f"ID: {c.id} | Name: {c.name}\n")

        f.write("\n=== EMPLOYEES ===\n")
        employees = Employee.objects.all()
        if not employees.exists():
            f.write("No employees found.\n")
        for e in employees:
            f.write(f"Emp ID: {e.id} | Name: {e.first_name} {e.last_name} | Email: {e.email} | Company: {e.company.name if e.company else 'None'} (ID: {e.company_id})\n")


if __name__ == "__main__":
    diagnose()
