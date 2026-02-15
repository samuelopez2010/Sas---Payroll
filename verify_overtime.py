
import os
import django
from decimal import Decimal
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import Company, User
from hr.models import Employee, Department, Position, Attendance
from payroll.models import PayrollPeriod, SalaryRule, TaxBracket
from payroll.services import PayrollCalculator

def verify_overtime():
    print("Verifying Overtime Calculation...")
    
    # 1. Setup Data
    company, _ = Company.objects.get_or_create(name="Test Corp", slug="test-corp")
    
    user, _ = User.objects.get_or_create(username="testadmin", email="admin@test.com", company=company)
    
    dept, _ = Department.objects.get_or_create(name="Engineering", company=company)
    pos, _ = Position.objects.get_or_create(title="Developer", department=dept, company=company)
    
    # Create Employee with $3200 salary
    # Hourly Rate approx: (3200 / 30) / 8 = 13.333
    # Overtime Rate: 13.333 * 1.5 = 20.00
    employee, created = Employee.objects.get_or_create(
        email="overtime.test@test.com",
        defaults={
            'first_name': "Overtime",
            'last_name': "Tester",
            'company': company,
            'position': pos,
            'department': dept,
            'hire_date': timezone.now().date(),
            'salary': Decimal('3200.00'),
            'bank_account': "123",
            'is_active': True
        }
    )
    
    # 2. Create Attendance: 10 hours work (9:00 - 19:00)
    # Overtime should be 2 hours.
    today = timezone.now().date()
    Attendance.objects.filter(employee=employee, date=today).delete() # Cleanup
    
    Attendance.objects.create(
        employee=employee,
        company=company,
        date=today,
        check_in=datetime.time(9, 0),
        check_out=datetime.time(19, 0)
    )
    
    # 3. Create Period
    period, _ = PayrollPeriod.objects.get_or_create(
        company=company,
        start_date=today - datetime.timedelta(days=1),
        end_date=today + datetime.timedelta(days=1)
    )
    
    # 4. Run Calculator
    calculator = PayrollCalculator(employee, period)
    data = calculator.calculate_net_pay()
    
    print("-" * 30)
    print(f"Hours Worked: {data['hours_worked']}")
    print(f"Overtime Hours: {data['overtime_hours']}")
    print(f"Overtime Pay: {data['overtime_pay']}")
    print(f"Gross Pay: {data['gross_pay']}")
    print("-" * 30)
    
    # 5. Verify
    # Expected: 2 hours overtime
    if data['overtime_hours'] == 2.0:
        print("PASS: Overtime Hours correct (2.0)")
    else:
        print(f"FAIL: Overtime Hours incorrect. Got {data['overtime_hours']}")
        
    # Expected Pay: 2 * 20.00 = 40.00
    # Hourly = 3200/240 = 13.3333...
    # Rate = 20.00...
    # Pay = 40.00
    if 39.0 < data['overtime_pay'] < 41.0:
         print(f"PASS: Overtime Pay correct approx ({data['overtime_pay']})")
    else:
         print(f"FAIL: Overtime Pay incorrect. Got {data['overtime_pay']}")

if __name__ == "__main__":
    verify_overtime()
