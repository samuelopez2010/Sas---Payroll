from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CompanyRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, help_text="Name of your organization")
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email')

from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'logo', 'primary_color')
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
        }
