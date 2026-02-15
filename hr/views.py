
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Employee, Attendance, Department, Position, LeaveRequest
from .forms import EmployeeForm, DepartmentForm, PositionForm, LeaveRequestForm, AttendanceForm
from core.decorators import hr_admin_required

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset.order_by('last_name')

class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('employee_list')
    
    def test_func(self):
        return self.request.user.is_hr_admin

    def form_valid(self, form):
        return super().form_valid(form)

class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('employee_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = 'hr/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')

    def test_func(self):
        return self.request.user.is_hr_admin

from django.views.generic import DetailView
from .models import EmployeeDocument
from .forms import EmployeeDocumentForm

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all().order_by('-uploaded_at')
        context['document_form'] = EmployeeDocumentForm()
        return context

class EmployeeDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = EmployeeDocument
    form_class = EmployeeDocumentForm
    template_name = 'hr/employee_detail.html' # Re-uses detail view technically, but usually we just post to endpoints

    def test_func(self):
         return self.request.user.is_hr_admin

    def form_valid(self, form):
        employee = get_object_or_404(Employee, pk=self.kwargs['employee_id'])
        form.instance.employee = employee
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'pk': self.kwargs['employee_id']})

class EmployeeDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = EmployeeDocument
    
    def test_func(self):
        return self.request.user.is_hr_admin

    def get_success_url(self):
        return reverse_lazy('employee_detail', kwargs={'pk': self.object.employee.pk})

# --- Department Views ---
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('department_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('department_list')

    def test_func(self):
        return self.request.user.is_hr_admin
    
class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Department
    template_name = 'hr/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')

    def test_func(self):
        return self.request.user.is_hr_admin

# --- Position Views ---
class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'hr/position_list.html'
    context_object_name = 'positions'

class PositionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('position_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class PositionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'hr/position_form.html'
    success_url = reverse_lazy('position_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class PositionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Position
    template_name = 'hr/position_confirm_delete.html'
    success_url = reverse_lazy('position_list')

    def test_func(self):
        return self.request.user.is_hr_admin

@login_required
def attendance_list(request):
    attendance = Attendance.objects.all().order_by('-date')
    return render(request, 'hr/attendance_list.html', {'attendance': attendance})

# --- Leave Management Views ---
class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'hr/leave_list.html'
    context_object_name = 'leaves'
    
    def get_queryset(self):
        # Admin sees all, Employee sees only their own
        if hasattr(self.request.user, 'is_employee_only') and self.request.user.is_employee_only:
             if hasattr(self.request.user, 'employee_profile'):
                 return LeaveRequest.objects.filter(employee=self.request.user.employee_profile).order_by('-start_date')
        return LeaveRequest.objects.all().order_by('-start_date')

class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'hr/leave_form.html'
    success_url = reverse_lazy('leave_list')

    def form_valid(self, form):
        if hasattr(self.request.user, 'employee_profile'):
            form.instance.employee = self.request.user.employee_profile
        return super().form_valid(form)

@login_required
def leave_approve(request, pk):
    # RBAC check could go here or via decorator
    if not getattr(request.user, 'is_hr_admin', False):
        from django.contrib import messages
        messages.error(request, "Access denied.")
        return redirect('leave_list')
        
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = 'APPROVED'
    leave.save()
    from django.contrib import messages
    messages.success(request, f"Leave request for {leave.employee} approved.")
    return redirect('leave_list')

@login_required
def leave_reject(request, pk):
    if not getattr(request.user, 'is_hr_admin', False):
        from django.contrib import messages
        messages.error(request, "Access denied.")
        return redirect('leave_list')
        
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = 'REJECTED'
    leave.save()
    from django.contrib import messages
    messages.warning(request, f"Leave request for {leave.employee} rejected.")
    return redirect('leave_list')

# --- Attendance Management Views ---
class AttendanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class AttendanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return self.request.user.is_hr_admin

class AttendanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Attendance
    template_name = 'hr/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance_list')

    def test_func(self):
        return self.request.user.is_hr_admin

# --- Timeclock Views ---
@login_required
def clock_in(request):
    if request.method == 'POST':
        # Assuming OneToOne link exists or using helper. 
        # If no strict link, we might fail. 
        # For now, let's try to get employee via reverse relation or loose query
        if hasattr(request.user, 'employee_profile'):
            employee = request.user.employee_profile
        else:
            # Fallback for demo: Pick first active employee
            employee = Employee.objects.filter(is_active=True).first()
        
        if not employee:
            from django.contrib import messages
            messages.error(request, "No employee profile found for this user.")
            return redirect('payroll_dashboard')

        # Check if already clocked in today
        today = timezone.now().date()
        existing = Attendance.objects.filter(employee=employee, date=today).first()
        
        from django.contrib import messages
        if existing:
            messages.warning(request, "You already have an attendance record for today.")
        else:
            Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=timezone.now().time()
            )
            messages.success(request, "Clocked in successfully.")
            
    return redirect('payroll_dashboard')

@login_required
def clock_out(request):
    if request.method == 'POST':
        if hasattr(request.user, 'employee_profile'):
            employee = request.user.employee_profile
        else:
             employee = Employee.objects.filter(is_active=True).first()

        if not employee:
             return redirect('payroll_dashboard')

        today = timezone.now().date()
        attendance = Attendance.objects.filter(employee=employee, date=today, check_out__isnull=True).first()
        
        from django.contrib import messages
        if attendance:
            attendance.check_out = timezone.now().time()
            attendance.save()
            messages.success(request, "Clocked out successfully.")
        else:
            messages.error(request, "No active check-in found for today.")
            
    return redirect('payroll_dashboard')
