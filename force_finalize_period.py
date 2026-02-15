
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from payroll.models import PayrollPeriod
from core.utils import set_current_company
from core.models import Company

def force_finalize():
    company = Company.objects.first()
    set_current_company(company)
    
    # Get latest period
    period = PayrollPeriod.objects.order_by('-end_date').first()
    if period:
        print(f"Found period: {period}")
        if not period.is_processed:
            period.is_processed = True
            period.save()
            print("✅ Successfully marked period as PROCESSED.")
        else:
            print("Period was already processed.")
    else:
        print("No period found to finalize.")

if __name__ == "__main__":
    force_finalize()
