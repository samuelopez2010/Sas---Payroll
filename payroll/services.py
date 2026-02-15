from decimal import Decimal
from django.db import models
from django.db.models import Q
from hr.models import Attendance
from .models import SalaryRule, Payslip, TaxBracket

class PayrollCalculator:
    def __init__(self, employee, period):
        self.employee = employee
        self.period = period

    def calculate_net_pay(self):
        # 1. Calculate Hours Worked
        attendance_records = Attendance.objects.filter(
            employee=self.employee,
            date__range=[self.period.start_date, self.period.end_date]
        )
        
        total_hours = 0
        total_overtime_hours = Decimal('0.0')
        for record in attendance_records:
            total_hours += record.get_hours_worked()
            total_overtime_hours += Decimal(record.get_overtime_hours())
            
        # 2. Calculate Base Pay & Overtime
        # Standard hours is usually 8 * 20 work days = 160 approx.
        # But for accurate calculating, we should trust total_hours if hourly.
        # Here we assume a fixed monthly salary.
        # Hourly Rate = (Monthly Salary / 30 days) / 8 hours
        hourly_rate = (self.employee.salary / Decimal('30')) / Decimal('8')
        
        # Base Pay is the Salary (assuming full attendance, but for MVP we pay full salary unless unpaid leave)
        # To keep it simple: Base Salary is fixed. Overtime is added on top.
        base_pay = self.employee.salary 
        
        overtime_pay = total_overtime_hours * (hourly_rate * Decimal('1.5'))
        
        gross_pay = base_pay + overtime_pay
        
        # 3. Apply Allowances
        rules = SalaryRule.objects.all()
        total_allowances = Decimal('0.00')
        other_deductions = Decimal('0.00') 
        
        for rule in rules:
            amount = Decimal('0.00')
            if rule.amount:
                amount = rule.amount
            elif rule.percentage:
                amount = gross_pay * (rule.percentage / Decimal('100.0'))
            
            if rule.rule_type == 'ALLOWANCE':
                total_allowances += amount
            elif rule.rule_type == 'DEDUCTION':
                other_deductions += amount
        
        total_gross = gross_pay + total_allowances
        
        # 4. Calculate Tax (ISLR / Progressive)
        # Formula: (Income * Rate) - Deduction
        tax_deduction = Decimal('0.00')
        active_bracket = TaxBracket.objects.filter(
            min_income__lte=total_gross
        ).filter(
            models.Q(max_income__gte=total_gross) | models.Q(max_income__isnull=True)
        ).first()
        
        if active_bracket:
            tax_rate = active_bracket.tax_rate / Decimal('100.0')
            tax_deduction = (total_gross * tax_rate) - active_bracket.deduction_amount
            if tax_deduction < 0:
                tax_deduction = Decimal('0.00')

        total_deductions = other_deductions + tax_deduction
        net_pay = total_gross - total_deductions
        
        return {
            'gross_pay': round(total_gross, 2), # Reporting Total Gross (Base + Allowances)
            'total_deductions': round(total_deductions, 2),
            'net_pay': round(net_pay, 2),
            'hours_worked': round(total_hours, 2),
            'overtime_hours': round(total_overtime_hours, 2),
            'overtime_pay': round(overtime_pay, 2)
        }
    
    def generate_payslip(self):
        data = self.calculate_net_pay()
        payslip = Payslip.objects.create(
            employee=self.employee,
            period=self.period,
            gross_pay=data['gross_pay'],
            total_deductions=data['total_deductions'],
            net_pay=data['net_pay'],
            overtime_hours=data['overtime_hours'],
            overtime_pay=data['overtime_pay']
        )
        return payslip
