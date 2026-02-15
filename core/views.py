from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CompanyRegistrationForm
from .models import Company

def register(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            # Create User but don't save yet (need to set company)
            user = form.save(commit=False)
            
            # Create Company
            company_name = form.cleaned_data['company_name']
            company = Company.objects.create(
                name=company_name,
                slug=company_name.lower().replace(' ', '-')
            )
            
            # Link User to Company
            user.company = company
            user.role = 'ADMIN' # Creator is always Admin
            user.save()
            
            # Log the user in
            login(request, user)
            
            return redirect('payroll_dashboard')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import CompanyForm

class CompanyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'core/company_settings.html'
    success_url = reverse_lazy('company_settings')

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, "Company settings updated successfully.")
        return super().form_valid(form)
    
    def get_object(self, queryset=None):
        # Always return the user's company
        if not self.request.user.company:
            # Handle edge case for Superusers or broken users
            # Option 1: Create a default company
            if self.request.user.is_superuser:
                 company, _ = Company.objects.get_or_create(name="Admin Company", slug="admin-company")
                 self.request.user.company = company
                 self.request.user.save()
                 return company
            # Option 2: Redirect or 404 (handled by view flow usually, but returning None crashes)
            # We must return an object or raise Http404
            from django.http import Http404
            raise Http404("No company assigned to this user.")
            
        return self.request.user.company

    def test_func(self):
        return self.request.user.is_hr_admin

    def handle_no_permission(self):
        return redirect('payroll_dashboard')
