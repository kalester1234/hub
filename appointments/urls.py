from django.urls import path
from . import views

urlpatterns = [
    path('browse/', views.browse_doctors, name='browse_doctors'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('<int:appointment_id>/prescription/', views.add_prescription, name='add_prescription'),
]