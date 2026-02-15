
from django.db import models
from django.utils import timezone
from core.models import TenantAwareModel
from datetime import timedelta

class Department(TenantAwareModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Position(TenantAwareModel):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='positions')
    
    def __str__(self):
        return self.title

class Employee(TenantAwareModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    # Enhanced Fields
    profile_image = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    CONTRACT_TYPES = (
        ('FULL_TIME', 'Full-Time'),
        ('PART_TIME', 'Part-Time'),
        ('CONTRACTOR', 'Contractor'),
        ('INTERN', 'Intern'),
    )
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, default='FULL_TIME')
    is_active = models.BooleanField(default=True)

    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account = models.CharField(max_length=50)

    def get_years_of_service(self):
        today = timezone.now().date()
        return (today - self.hire_date).days // 365

    def get_vacation_days_total(self):
        """
        Calculates total vacation days entitlement based on years of service.
        Logic: 15 days base + 1 additional day for each year of service after the first.
        Maximum is usually capped (e.g. 30 days total), but leaving uncapped for now unless specified.
        """
        years = self.get_years_of_service()
        # If less than 1 year, maybe 0? Or pro-rated? 
        # User said "15 days base". Let's assume 15 days available from start or after year 1.
        # Impl: 15 days + 1 for every year past year 1.
        additional_days = max(0, years - 1)
        return 15 + additional_days

    def get_vacation_days_used(self):
        approved_leaves = self.leaverequest_set.filter(status='APPROVED', leave_type='VACATION')
        total_days = 0
        for leave in approved_leaves:
            # Simple day diff + 1 (inclusive)
            # Todo: Exclude weekends? Keeping simple for now.
            days = (leave.end_date - leave.start_date).days + 1
            total_days += days
        return total_days

    def get_vacation_balance(self):
        return self.get_vacation_days_total() - self.get_vacation_days_used()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class LeaveRequest(TenantAwareModel):
    LEAVE_TYPES = (
        ('VACATION', 'Vacation'),
        ('SICK', 'Sick Leave'),
        ('UNPAID', 'Unpaid Leave'),
        ('OTHER', 'Other'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='VACATION')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def get_duration(self):
        return (self.end_date - self.start_date).days + 1
        
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date})"

class Attendance(TenantAwareModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    
    def get_hours_worked(self):
        if self.check_in and self.check_out:
            # Combine date with times to create datetime objects
            # Note: This assumes check_in and check_out are on the same day. 
            # Handling overnight shifts would require more complex logic.
            start = timezone.datetime.combine(self.date, self.check_in)
            end = timezone.datetime.combine(self.date, self.check_out)
            duration = end - start
            return duration.total_seconds() / 3600 # hours
        return 0

    def get_overtime_hours(self):
        hours = self.get_hours_worked()
        # Overtime is anything > 8 hours
        return max(0, hours - 8)

    @property
    def is_late(self):
        # Placeholder for late arrival logic based on shift schedule
        # Assuming a standard start time of 9:00 AM for simplicity or fetched from a Schedule model
        SCHED_START = timezone.datetime.strptime("09:00", "%H:%M").time()
        return self.check_in > SCHED_START

class EmployeeDocument(TenantAwareModel):
    DOC_TYPES = (
        ('CONTRACT', 'Contract'),
        ('ID', 'Identification'),
        ('RESUME', 'Resume/CV'),
        ('OTHER', 'Other'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPES, default='OTHER')
    file = models.FileField(upload_to='employee_docs/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.employee}"
