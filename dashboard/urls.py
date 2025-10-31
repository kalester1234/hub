from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('appointments/<int:appointment_id>/status/', views.admin_update_appointment_status, name='admin_update_appointment_status'),
]