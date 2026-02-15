
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from hr.models import Employee

def find_employee():
    email = "alejandrolopezb2019@gmail.com"
    print(f"Searching for: {email}")
    
    employees = Employee.objects.filter(email=email)
    
    if employees.exists():
        for emp in employees:
            print(f"FOUND: ID={emp.id}, Name={emp.first_name} {emp.last_name}, Company={emp.company.name} (ID: {emp.company.id}), Active={emp.is_active}")
    else:
        print("No employee found with this email.")

if __name__ == "__main__":
    find_employee()
