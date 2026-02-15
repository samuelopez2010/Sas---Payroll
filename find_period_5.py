
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from payroll.models import PayrollPeriod
from core.models import Company
from core.utils import set_current_company

def find_and_fix_period_5():
    print("--- Searching for Period ID 5 ---")
    
    companies = Company.objects.all()
    target_found = False
    
    for company in companies:
        set_current_company(company)
        try:
            p = PayrollPeriod.objects.get(id=5)
            print(f"✅ FOUND in Company: {company.name} (ID: {company.id})")
            print(f"   Period: {p.start_date} to {p.end_date}")
            print(f"   Current Status: Processed={p.is_processed}")
            
            if not p.is_processed:
                p.is_processed = True
                p.save()
                print("   ✅ FIXED: Marked as PROCESSED.")
            else:
                print("   ℹ️ Already processed.")
            target_found = True
            break
        except PayrollPeriod.DoesNotExist:
            continue
            
    if not target_found:
        print("❌ Period ID 5 not found in any company context.")

if __name__ == "__main__":
    find_and_fix_period_5()
