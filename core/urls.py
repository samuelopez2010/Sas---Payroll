from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('settings/', views.CompanyUpdateView.as_view(), name='company_settings'),
]
