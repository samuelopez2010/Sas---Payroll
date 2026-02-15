
from django.db import models
from core.models import TenantAwareModel
from hr.models import Employee

from core.utils import get_current_company

class PayrollPeriod(TenantAwareModel):
    start_date = models.DateField()
    end_date = models.DateField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"

class SalaryRule(TenantAwareModel):
    RULE_TYPES = (
        ('ALLOWANCE', 'Allowance'),
        ('DEDUCTION', 'Deduction'),
    )
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Percentage of Base Salary
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Percentage of Base Salary
    
    # Assignment Logic
    is_global = models.BooleanField(default=True, help_text="If checked, applies to ALL employees.")
    assigned_employees = models.ManyToManyField(Employee, blank=True, related_name='salary_rules', help_text="If not global, only applies to selected employees.")

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"

class TaxBracket(TenantAwareModel):
    """
    Defines a progressive tax bracket.
    Example ISLR or similar:
    0 - 1000 : 0%
    1001 - 2000 : 10%
    2001+ : 20%
    """
    min_income = models.DecimalField(max_digits=10, decimal_places=2)
    max_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Leave blank for infinity")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (e.g. 15.00 for 15%)")
    deduction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, help_text="Auto-calculated if left blank")

    def save(self, *args, **kwargs):
        if not self.company_id:
             self.company = get_current_company()

        # Auto-calculate Sustraendo if not provided
        # Formula: (Previous_Max * Current_Rate) - Previous_Total_Tax
        if self.deduction_amount == 0 and self.min_income > 0:
            from decimal import Decimal
            # Find previous brackets
            previous_brackets = TaxBracket.objects.filter(
                company=self.company,
                max_income__lt=self.min_income
            ).order_by('min_income')
            
            if previous_brackets.exists():
                previous_max = previous_brackets.last().max_income
                if previous_max:
                    # Calculate tax on previous_max amount using those brackets
                    previous_tax = Decimal('0.00')
                    remainder = previous_max
                    
                    for bracket in previous_brackets:
                        # Portion of income in this bracket
                        bracket_limit = bracket.max_income if bracket.max_income else remainder
                        # But since we are iterating ordered, max_income should exist for all except last (which matches previous_max)
                        
                        # Actually simpler: standard tax calc logic
                        # But we can't easily import PayrollCalculator here due to circular imports.
                        # Let's do raw math.
                        start = bracket.min_income
                        end = bracket.max_income
                        
                        # Ensure we don't go past the target (previous_max)
                        if end > previous_max:
                            end = previous_max
                            
                        taxable_in_bracket = end - start
                        if taxable_in_bracket > 0:
                            previous_tax += taxable_in_bracket * (bracket.tax_rate / Decimal('100.0'))
                            
                    # Now calculate theoretical tax at current rate for that same amount
                    theoretical_tax = previous_max * (self.tax_rate / Decimal('100.0'))
                    
                    self.deduction_amount = theoretical_tax - previous_tax

        super().save(*args, **kwargs)

    def __str__(self):
        max_val = self.max_income if self.max_income else "Infinity"
        return f"{self.min_income} - {max_val} : {self.tax_rate}%"

    class Meta:
        ordering = ['min_income']

class Payslip(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # We can store a JSON field for the breakdown of rules applied if needed
    # rules_breakdown = models.JSONField(default=dict)

    def __str__(self):
        return f"Payslip for {self.employee} - {self.period}"
