from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('appointments/<int:appointment_id>/status/', views.admin_update_appointment_status, name='admin_update_appointment_status'),
]