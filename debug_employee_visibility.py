
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import Company, User
from hr.models import Employee
from core.utils import set_current_company, remove_current_company


def debug_visibility():
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        f.write("--- Debugging Employee Visibility ---\n")
        
        # 1. List all companies
        companies = Company.objects.all()
        f.write(f"Total Companies: {companies.count()}\n")
        for c in companies:
            f.write(f" - {c.name} (ID: {c.id})\n")

        # 2. List all users and their companies
        users = User.objects.all()
        f.write(f"\nTotal Users: {users.count()}\n")
        for u in users:
            company_name = u.company.name if u.company else "None"
            f.write(f" - {u.username} (ID: {u.id}) -> Company: {company_name}\n")

        # 3. Check for Orphaned Employees
        remove_current_company() # Ensure clean state
        orphans = Employee.objects.filter(company__isnull=True)
        f.write(f"\n--- Orphaned Employees (No Company) ---\n")
        f.write(f"Count: {orphans.count()}\n")
        for e in orphans:
             f.write(f" - {e.first_name} {e.last_name} (ID: {e.id})\n")

        # 4. Find the most recent employee added
        f.write("\n--- Employees by Company Context ---\n")
        
        for c in companies:
            set_current_company(c)
            f.write(f"\nContext: {c.name}\n")
            emps = Employee.objects.all()
            f.write(f"Employees visible: {emps.count()}\n")
            for e in emps:
                 f.write(f" - {e.first_name} {e.last_name} (ID: {e.id})\n")

if __name__ == "__main__":
    debug_visibility()
