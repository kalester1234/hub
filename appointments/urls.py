from django.urls import path
from . import views

urlpatterns = [
    path('browse/', views.browse_doctors, name='browse_doctors'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('chatbot/suggest-slot/', views.chatbot_suggest_slot, name='chatbot_suggest_slot'),
    path('chatbot/book/', views.chatbot_book_appointment, name='chatbot_book_appointment'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('<int:appointment_id>/prescription/', views.add_prescription, name='add_prescription'),
    path('<int:appointment_id>/prescription/edit/', views.edit_prescription, name='edit_prescription'),
    path('<int:appointment_id>/prescription/download/', views.download_prescription, name='download_prescription'),
    path('leave/request/', views.request_leave, name='request_leave'),
    path('leave/manage/', views.manage_leave_requests, name='manage_leave_requests'),
    path('api/template-items/<int:template_id>/', views.get_template_items, name='get_template_items'),
]