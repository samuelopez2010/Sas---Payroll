
import os
import django
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staffcore.settings')
django.setup()

from payroll.models import PayrollPeriod, Payslip
from core.utils import set_current_company
from core.models import Company

def debug_chart():
    # Set context to first company (likely the user's)
    company = Company.objects.first()
    if not company:
        print("No company found.")
        return
    set_current_company(company)
    print(f"Debug Context: Company = {company.name}")

    print("\n--- Payroll Periods ---")
    periods = PayrollPeriod.objects.all().order_by('-end_date')
    if not periods.exists():
        print("No periods found.")
    
    for p in periods:
        payslips_count = Payslip.objects.filter(period=p).count()
        total_net = Payslip.objects.filter(period=p).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        print(f"ID: {p.id} | {p.start_date} - {p.end_date} | Processed: {p.is_processed} | Payslips: {payslips_count} | Total Net: ${total_net}")

    print("\n--- Chart Data Logic (Simulated) ---")
    last_periods = PayrollPeriod.objects.filter(is_processed=True).order_by('-end_date')[:6]
    last_periods = list(last_periods)[::-1]
    
    if not last_periods:
        print("Chart Data: EMPTY (No processed periods found)")
    else:
        for p in last_periods:
            cost = Payslip.objects.filter(period=p).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
            print(f"Chart Entry: {p.end_date} -> ${cost}")

if __name__ == "__main__":
    debug_chart()
