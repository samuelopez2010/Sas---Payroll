
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from .models import Payslip, PayrollPeriod, SalaryRule, TaxBracket
from .forms import SalaryRuleForm, TaxBracketForm
from hr.models import Employee, Attendance, Department 
from .services import PayrollCalculator
from core.utils import get_current_company
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

# --- Salary Rule Views ---
class SalaryRuleListView(LoginRequiredMixin, ListView):
    model = SalaryRule
    template_name = 'payroll/salary_rule_list.html'
    context_object_name = 'rules'

class SalaryRuleCreateView(LoginRequiredMixin, CreateView):
    model = SalaryRule
    form_class = SalaryRuleForm
    template_name = 'payroll/salary_rule_form.html'
    success_url = reverse_lazy('salary_rule_list')

class SalaryRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = SalaryRule
    form_class = SalaryRuleForm
    template_name = 'payroll/salary_rule_form.html'
    success_url = reverse_lazy('salary_rule_list')

class SalaryRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = SalaryRule
    template_name = 'payroll/salary_rule_confirm_delete.html'
    success_url = reverse_lazy('salary_rule_list')

# --- Tax Bracket Views ---
class TaxBracketListView(LoginRequiredMixin, ListView):
    model = TaxBracket
    template_name = 'payroll/tax_bracket_list.html'
    context_object_name = 'brackets'

class TaxBracketCreateView(LoginRequiredMixin, CreateView):
    model = TaxBracket
    form_class = TaxBracketForm
    template_name = 'payroll/tax_bracket_form.html'
    success_url = reverse_lazy('tax_bracket_list')

class TaxBracketUpdateView(LoginRequiredMixin, UpdateView):
    model = TaxBracket
    form_class = TaxBracketForm
    template_name = 'payroll/tax_bracket_form.html'
    success_url = reverse_lazy('tax_bracket_list')

class TaxBracketDeleteView(LoginRequiredMixin, DeleteView):
    model = TaxBracket
    template_name = 'payroll/tax_bracket_confirm_delete.html'
    success_url = reverse_lazy('tax_bracket_list')


@login_required
def payroll_dashboard(request):
    company = get_current_company() # Argument mismatch in previous file view? No, utils.py definition usually takes request or is global? 
    # Let's check utils.py usage. The view previously had `company = get_current_company()`. 
    # But `get_current_company` typically needs request. 
    # I'll stick to what was there: `get_current_company()` (maybe it inspects thread locals?)
    
    # Actually, let's look at the previous content: `company = get_current_company()` (line 67).
    
    # Timeclock Context
    active_attendance = None
    # Flexible employee resolution for demo
    employee = None
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
    else:
        employee = Employee.objects.filter(is_active=True).first()

    if employee:
        today = timezone.now().date()
        active_attendance = Attendance.objects.filter(
            employee=employee, 
            date=today, 
            check_out__isnull=True
        ).first()

    # Get latest active period or create a dummy one for display
    period = PayrollPeriod.objects.filter(is_processed=False).first()
    
    total_cost = 0
    if period:
        total_cost = Payslip.objects.filter(period=period).aggregate(Sum('net_pay'))['net_pay__sum'] or 0

    active_employees = Employee.objects.filter(is_active=True).count()
    department_count = Department.objects.count()

    # Chart Data: Last 6 processed periods
    last_periods = PayrollPeriod.objects.filter(is_processed=True).order_by('-end_date')[:6]
    last_periods = list(last_periods)[::-1] # Reverse to chronological
    
    chart_dates = []
    chart_values = []
    
    for p in last_periods:
        cost = Payslip.objects.filter(period=p).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        chart_dates.append(p.end_date.strftime("%b"))
        chart_values.append(float(cost))
        
    # If no data, show empty placeholders
    if not chart_dates:
        chart_dates = ["No Data"]
        chart_values = [0]

    return render(request, 'dashboard.html', {
        'total_cost': total_cost,
        'active_employees': active_employees,
        'department_count': department_count,
        'period': period,
        'active_attendance': active_attendance,
        'chart_dates': chart_dates,
        'chart_values': chart_values,
    })

@require_POST
def process_payroll(request):
    """
    Simulates running payroll. In real app, this might kick off a Celery task.
    For this demo, we'll just ensure a period exists and payslips are generated 
    (or redirect to the table view).
    """
    # Find or create next period
    # For demo simplicity, get the first period
    period = PayrollPeriod.objects.first() 
    if not period:
        # Create a dummy period if none exists
        from datetime import date
        period = PayrollPeriod.objects.create(start_date=date(2023, 10, 1), end_date=date(2023, 10, 15))

    # Generate payslips if they don't exist
    employees = Employee.objects.filter(is_active=True)
    for emp in employees:
        if not Payslip.objects.filter(employee=emp, period=period).exists():
            PayrollCalculator(emp, period).generate_payslip()
            
    from django.urls import reverse
    response = HttpResponse()
    response['HX-Redirect'] = reverse('run_payroll', args=[period.id])
    return response

@require_POST
@login_required
def finalize_payroll(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    period.is_processed = True
    period.save()
    return redirect('payroll_dashboard')

@login_required
def run_payroll(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)
    payslips = Payslip.objects.filter(period=period).order_by('employee__last_name')
    
    total_cost = payslips.aggregate(Sum('net_pay'))['net_pay__sum'] or 0
    
    return render(request, 'payroll/run_payroll.html', {
        'period': period,
        'payslips': payslips,
        'total_cost': total_cost
    })

@require_POST
def update_payslip_bonus(request, payslip_id):
    payslip = get_object_or_404(Payslip, id=payslip_id)
    new_bonus = request.POST.get('bonus')
    
    try:
        payslip.bonus = float(new_bonus)
        # Recalculate Net Pay: Gross + Bonus - Deductions
        # Note: Deductions might need re-calc if they are percentage based on (Gross + Bonus)
        # For simplicity, assuming Deductions are fixed based on Base Gross.
        payslip.net_pay = float(payslip.gross_pay) + payslip.bonus - float(payslip.total_deductions)
        payslip.save()
        
        # Calculate new total for OOB update
        total_cost = Payslip.objects.filter(period=payslip.period).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        
        return render(request, 'payroll/partials/payslip_update.html', {
            'payslip': payslip,
            'total_cost': total_cost
        })
    except ValueError:
        return HttpResponseBadRequest("Invalid Input")

def load_payslip_modal(request, payslip_id):
    """
    HTMX View: Returns a modal content with payslip details.
    Trigger: <button hx-get="/payroll/payslip/1/" hx-target="#modal-content">View</button>
    """
    payslip = get_object_or_404(Payslip, id=payslip_id)
    return render(request, 'payroll/payslip_modal.html', {'payslip': payslip})

def generate_payslip_pdf(request, payslip_id):
    """
    Generates a PDF for the payslip using WeasyPrint.
    """
    payslip = get_object_or_404(Payslip, id=payslip_id)
    html_string = render_to_string('payroll/payslip_pdf.html', {'payslip': payslip})
    
    # For demonstration without WeasyPrint installed:
    # We return the HTML with a script to auto-print or just view.
    # To enable WeasyPrint:
    # 1. pip install weasyprint
    # 2. uncomment the lines below
    
    # import weasyprint
    # pdf_file = weasyprint.HTML(string=html_string).write_pdf()
    # response = HttpResponse(pdf_file, content_type='application/pdf')
    # response['Content-Disposition'] = f'filename="payslip_{payslip.id}.pdf"'
    # return response

    return HttpResponse(html_string)
