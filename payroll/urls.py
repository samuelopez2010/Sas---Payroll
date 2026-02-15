
from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_dashboard, name='payroll_dashboard'),
    path('process/', views.process_payroll, name='process_payroll'),
    path('run/<int:period_id>/', views.run_payroll, name='run_payroll'),
    path('run/<int:period_id>/finalize/', views.finalize_payroll, name='finalize_payroll'),
    path('payslip/<int:payslip_id>/update-bonus/', views.update_payslip_bonus, name='update_payslip_bonus'),
    path('payslip/<int:payslip_id>/', views.load_payslip_modal, name='load_payslip_modal'),
    path('payslip/<int:payslip_id>/pdf/', views.generate_payslip_pdf, name='generate_payslip_pdf'),
    
    # Configuration
    path('rules/', views.SalaryRuleListView.as_view(), name='salary_rule_list'),
    path('rules/add/', views.SalaryRuleCreateView.as_view(), name='salary_rule_add'),
    path('rules/<int:pk>/edit/', views.SalaryRuleUpdateView.as_view(), name='salary_rule_edit'),
    path('rules/<int:pk>/delete/', views.SalaryRuleDeleteView.as_view(), name='salary_rule_delete'),
    
    path('taxes/', views.TaxBracketListView.as_view(), name='tax_bracket_list'),
    path('taxes/add/', views.TaxBracketCreateView.as_view(), name='tax_bracket_add'),
    path('taxes/<int:pk>/edit/', views.TaxBracketUpdateView.as_view(), name='tax_bracket_edit'),
    path('taxes/<int:pk>/delete/', views.TaxBracketDeleteView.as_view(), name='tax_bracket_delete'),
]
