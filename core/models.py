
from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_current_company

class Company(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#000000', help_text="Hex code for primary branding color")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'HR Admin'),
        ('EMPLOYEE', 'Employee'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    @property
    def is_hr_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
        
    @property
    def is_employee_only(self):
        return self.role == 'EMPLOYEE' and not self.is_superuser

class TenantAwareManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_current_company()
        
        if company:
            return queryset.filter(company=company)
        
        return queryset

class TenantAwareModel(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='%(class)s_related')
    
    objects = TenantAwareManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.company_id:
            company = get_current_company()
            if company:
                self.company = company
        super().save(*args, **kwargs)
