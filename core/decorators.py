from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def hr_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_hr_admin:
            messages.error(request, "Access denied. You must be an HR Admin.")
            return redirect('payroll_dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
