
from celery import shared_task
from core.models importCompany
from .models import PayrollPeriod, Employee
from .services import PayrollCalculator

@shared_task
def process_bulk_payroll(period_id, company_id):
    """
    Processes payroll for all active employees in a company for a given period.
    """
    try:
        company = Company.objects.get(id=company_id)
        period = PayrollPeriod.objects.get(id=period_id)
        
        # Ensure we are in the correct tenant context if needed, 
        # but since we are filtering by company explicitly in the query, 
        # we might just need to pass the employee objects.
        # However, our models are TenantAware, so we might need to mock the request/context 
        # OR use a context manager to set the tenant for this thread.
        from core.utils import set_current_company, remove_current_company
        set_current_company(company)
        
        employees = Employee.objects.filter(company=company, is_active=True)
        results = []
        
        for employee in employees:
            calculator = PayrollCalculator(employee, period)
            payslip = calculator.generate_payslip()
            results.append(payslip.id)
            
        period.is_processed = True
        period.save()
        
        remove_current_company()
        return f"Successfully processed {len(results)} payslips for {company.name}"
        
    except Exception as e:
        return f"Error processing payroll: {str(e)}"
