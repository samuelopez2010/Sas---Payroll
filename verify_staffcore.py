
import os
import django
from decimal import Decimal
from datetime import date, time

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import Company, User
from core.utils import set_current_company, remove_current_company
from hr.models import Department, Position, Employee, Attendance
from payroll.models import SalaryRule, PayrollPeriod, Payslip
from payroll.services import PayrollCalculator

def test_multi_tenancy():
    print("\n--- Testing Multi-Tenancy Isolation ---")
    
    # 1. Create Companies
    company_a = Company.objects.create(name="Acme Corp", slug="acme")
    company_b = Company.objects.create(name="Globex", slug="globex")
    print(f"Created Companies: {company_a}, {company_b}")

    # 2. Add Employee to Company A
    # Context: Company A
    set_current_company(company_a)
    emp_a = Employee.objects.create(
        first_name="Alice",
        last_name="Smith",
        email="alice@acme.com",
        hire_date=date(2023, 1, 1),
        salary=Decimal('5000.00'), # Monthly
        bank_account="123456"
    )
    print(f"Created Employee in {company_a}: {emp_a}")
    
    # Verify we can see her
    count_a = Employee.objects.count()
    print(f"Employee count in context {company_a}: {count_a} (Expected: 1)")
    assert count_a == 1

    # Switch Context to Company B
    set_current_company(company_b)
    print(f"Switched context to {company_b}")
    
    # Verify we CANNOT see Alice
    count_b = Employee.objects.count()
    print(f"Employee count in context {company_b}: {count_b} (Expected: 0)")
    assert count_b == 0
    
    # Try to access specific object (should fail or not be found via manager)
    # Standard get() uses the manager, so it should fail.
    try:
        Employee.objects.get(id=emp_a.id)
        print("ERROR: Leaked Employee A in Context B!")
    except Employee.DoesNotExist:
        print("SUCCESS: Cannot access Employee A in Context B.")
        
    remove_current_company()

def test_payroll_calculation():
    print("\n--- Testing Payroll Calculation ---")
    
    company = Company.objects.get(slug="acme")
    set_current_company(company)
    
    emp = Employee.objects.get(email="alice@acme.com")
    
    # 1. Create Payroll Period
    period = PayrollPeriod.objects.create(
        start_date=date(2023, 9, 1),
        end_date=date(2023, 9, 15)
    )
    print(f"Created Period: {period}")
    
    # 2. Add Attendance (80 hours work)
    # 10 days * 8 hours
    for i in range(1, 11):
        Attendance.objects.create(
            employee=emp,
            date=date(2023, 9, i),
            check_in=time(9, 0),
            check_out=time(17, 0)
        )
    print("Added 10 days of attendance (80 hours).")
    
    # 3. Add Salary Rules
    # Allowance: Transport ($100 flat)
    SalaryRule.objects.create(
        name="Transport Allowance",
        rule_type='ALLOWANCE',
        amount=Decimal('100.00')
    )
    # Deduction: Tax (10% of gross)
    SalaryRule.objects.create(
        name="Income Tax",
        rule_type='DEDUCTION',
        percentage=Decimal('10.00')
    )
    print("Added Salary Rules: Transport ($100), Tax (10%).")
    
    # 4. Run Calculator
    # Expected:
    # Hourly Rate = 5000 / 160 = 31.25
    # Gross Base = 80 * 31.25 = 2500.00
    # Total Gross = 2500 + 100 = 2600.00
    # Tax = 2500 * 10% = 250.00 (Wait, tax on Base or Total Gross? Service implementation: gross_pay * percentage. gross_pay is base.)
    # Let's check logic in service: `amount = gross_pay * (rule.percentage...`. Correct, uses base gross_pay.
    # Tax = 2500 * 0.10 = 250.00.
    # Net = 2600 - 250 = 2350.00
    
    calculator = PayrollCalculator(emp, period)
    slip = calculator.generate_payslip()
    
    print(f"\nGenerated Payslip: {slip}")
    print(f"Gross Pay: {slip.gross_pay} (Expected: ~2600.00)")
    print(f"Deductions: {slip.total_deductions} (Expected: ~250.00)")
    print(f"Net Pay: {slip.net_pay} (Expected: ~2350.00)")
    
    assert slip.net_pay == Decimal('2350.00')
    print("SUCCESS: Net Pay matches expected value.")

    remove_current_company()

if __name__ == "__main__":
    try:
        test_multi_tenancy()
        test_payroll_calculation()
        print("\nAll Tests Passed!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
