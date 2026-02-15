
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from payroll.models import PayrollPeriod
from core.models import Company

def list_all_periods():
    print("--- Listing ALL Payroll Periods (ignoring tenant filter) ---")
    # Bypass tenant manager by using raw SQL or iterating companies
    
    companies = Company.objects.all()
    for company in companies:
        print(f"\nCompany: {company.name} (ID: {company.id})")
        # We need to manually filter because TenantAwareManager forces current_company
        # But we can set the context for each
        from core.utils import set_current_company
        set_current_company(company)
        
        periods = PayrollPeriod.objects.all()
        for p in periods:
             print(f"  - Period ID: {p.id} | {p.start_date} to {p.end_date} | Processed: {p.is_processed}")

if __name__ == "__main__":
    list_all_periods()
