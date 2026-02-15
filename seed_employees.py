
import os
import django
import traceback
from datetime import date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import Company
from hr.models import Employee, Department, Position

def seed():
    try:
        print("Starting seed...")
        company = Company.objects.get(slug="demo")
        print(f"Found company: {company}")
        
        dept, _ = Department.objects.get_or_create(name="Engineering", company=company)
        print(f"Dept: {dept}")
        
        pos, _ = Position.objects.get_or_create(title="Developer", department=dept, company=company)
        print(f"Pos: {pos}")
        
        # Try simple create
        if not Employee.objects.filter(email='alice_test@demo.com').exists():
            Employee.objects.create(
                first_name="Alice",
                last_name="Test",
                email="alice_test@demo.com",
                company=company,
                position=pos,
                department=dept,
                hire_date=date(2023, 1, 1),
                salary=Decimal('5000.00'),
                bank_account='123',
                contract_type='FULL_TIME',
                is_active=True
            )
            print("Created Alice Test")
        else:
            print("Alice Test exists")
            
        # Add Bob
        if not Employee.objects.filter(email='bob_test@demo.com').exists():
            Employee.objects.create(
                first_name="Bob",
                last_name="Builder",
                email="bob_test@demo.com",
                company=company,
                position=pos,
                department=dept,
                hire_date=date(2023, 2, 1),
                salary=Decimal('5200.00'),
                bank_account='456',
                contract_type='FULL_TIME',
                is_active=True
            )
            print("Created Bob Builder")
            
        # Add Charlie
        dept_hr, _ = Department.objects.get_or_create(name="Human Resources", company=company)
        pos_mgr, _ = Position.objects.get_or_create(title="HR Manager", department=dept_hr, company=company)
        
        if not Employee.objects.filter(email='charlie_test@demo.com').exists():
            Employee.objects.create(
                first_name="Charlie",
                last_name="Day",
                email="charlie_test@demo.com",
                company=company,
                position=pos_mgr,
                department=dept_hr,
                hire_date=date(2023, 3, 1),
                salary=Decimal('4500.00'),
                bank_account='789',
                contract_type='FULL_TIME',
                is_active=True
            )
            print("Created Charlie Day")
            
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    seed()
