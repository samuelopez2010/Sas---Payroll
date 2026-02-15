
import os
import django
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from payroll.models import PayrollPeriod, Payslip
from core.utils import set_current_company
from core.models import Company

def fix_specific_period():
    company = Company.objects.first()
    set_current_company(company)
    print(f"Company: {company.name}")
    
    # Target the October period seen in the screenshot
    # Check for ID 5 specifically since we saw it in previous debug
    try:
        period = PayrollPeriod.objects.get(id=5)
        print(f"Targeting Period ID 5: {period.start_date} to {period.end_date}")
        
        payslip_count = Payslip.objects.filter(period=period).count()
        total_net = Payslip.objects.filter(period=period).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        
        print(f"  - Payslips: {payslip_count}")
        print(f"  - Total Net: ${total_net}")
        print(f"  - Current processed status: {period.is_processed}")
        
        if not period.is_processed:
            period.is_processed = True
            period.save()
            print("  ✅ FIXED: Period ID 5 is now marked as PROCESSED.")
        else:
            print("  ℹ️ Period ID 5 was already processed.")
            
    except PayrollPeriod.DoesNotExist:
        print("❌ Period ID 5 not found. Searching by date...")
        period = PayrollPeriod.objects.filter(start_date__year=2023, start_date__month=10).first()
        if period:
             print(f"Found alternative period: {period.id} ({period.start_date} - {period.end_date})")
             period.is_processed = True
             period.save()
             print(f"  ✅ FIXED: Period {period.id} marked as PROCESSED.")
        else:
            print("❌ No matching period found.")

if __name__ == "__main__":
    fix_specific_period()
