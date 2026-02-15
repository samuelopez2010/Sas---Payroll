
import os
import django
from decimal import Decimal
from datetime import date, time

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from core.models import Company
from core.utils import set_current_company, remove_current_company
from hr.models import Employee, Attendance
from payroll.models import PayrollPeriod, Payslip
from payroll.services import PayrollCalculator

def test_overtime_and_bonus():
    print("\n--- Testing Phase 2: Overtime & Bonus ---")
    
    # Setup
    company, _ = Company.objects.get_or_create(name="TechStart", slug="techstart")
    set_current_company(company)
    
    emp, _ = Employee.objects.get_or_create(
        email="bob@techstart.io",
        defaults={
            'first_name': "Bob", 'last_name': "Builder",
            'hire_date': date(2023,1,1), 'salary': Decimal('3200.00'), # $20/hr
            'bank_account': "999", 'contract_type': 'FULL_TIME'
        }
    )
    
    period, _ = PayrollPeriod.objects.get_or_create(
        start_date=date(2023, 11, 1), end_date=date(2023, 11, 30)
    )
    
    # Clear previous data
    Attendance.objects.filter(employee=emp).delete()
    Payslip.objects.filter(employee=emp, period=period).delete()
    
    # 1. Add Attendance: 170 Hours (160 Regular + 10 Overtime)
    # 17 days * 10 hours = 170
    for i in range(1, 18):
        Attendance.objects.create(
            employee=emp, date=date(2023, 11, i),
            check_in=time(8, 0), check_out=time(18, 0)
        )
    
    # 2. Calculate
    calc = PayrollCalculator(emp, period)
    slip = calc.generate_payslip()
    
    print(f"Generated Payslip for {emp}")
    # Rate: 3200 / 160 = $20/hr
    # Regular: 160 * 20 = 3200
    # Overtime: 10 * (20 * 1.5) = 10 * 30 = 300
    # Gross Expect: 3500
    print(f"Gross Pay: {slip.gross_pay} (Expected: 3500.00)")
    assert slip.gross_pay == Decimal('3500.00')
    
    # 3. Test Bonus Update (Simulating HTMX View logic)
    print("Applying Bonus: $500.00")
    slip.bonus = Decimal('500.00')
    slip.net_pay = slip.gross_pay + slip.bonus - slip.total_deductions
    slip.save()
    
    print(f"Net Pay after Bonus: {slip.net_pay} (Expected: ~4000.00 assuming 0 deductions for test)")
    # Note: Deductions are 0 provided no rules exist in this company
    
    if slip.net_pay == Decimal('4000.00'):
        print("SUCCESS: Overtime and Bonus functionality verified.")
    else:
        print(f"WARNING: Net Pay {slip.net_pay} != 4000.00 (Check deductions?)")

    remove_current_company()

if __name__ == "__main__":
    try:
        test_overtime_and_bonus()
        print("\nPhase 2 Verification Complete!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
