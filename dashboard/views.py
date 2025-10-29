from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from messaging.models import Notification
from accounts.models import DoctorProfile

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard view - role-based"""
    user = request.user
    
    if user.role == 'doctor':
        return doctor_dashboard(request)
    elif user.role == 'patient':
        return patient_dashboard(request)
    elif user.role == 'admin':
        return admin_dashboard(request)
    else:
        return patient_dashboard(request)

def doctor_dashboard(request):
    """Doctor dashboard"""
    doctor = request.user
    
    # Get appointments statistics
    today = timezone.now().date()
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status='confirmed'
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today,
        status='confirmed'
    ).count()
    
    pending_requests = Appointment.objects.filter(
        doctor=doctor,
        status='pending'
    ).count()
    
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='completed'
    ).count()
    
    # Get notifications
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    
    # Get unread messages
    from messaging.models import Message, Conversation
    conversations = Conversation.objects.filter(doctor=doctor)
    unread_messages = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=doctor).count()
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'pending_requests': pending_requests,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'dashboard/doctor_dashboard.html', context)

def patient_dashboard(request):
    """Patient dashboard"""
    patient = request.user
    
    # Get appointments statistics
    today = timezone.now().date()
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=today,
        status='confirmed'
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    today_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date=today,
        status='confirmed'
    ).count()
    
    total_appointments = Appointment.objects.filter(patient=patient).count()
    completed_appointments = Appointment.objects.filter(
        patient=patient,
        status='completed'
    ).count()
    
    # Get doctors
    from accounts.models import CustomUser
    doctors = CustomUser.objects.filter(role='doctor', doctor_profile__is_approved=True).count()
    
    # Get notifications
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    
    # Get unread messages
    from messaging.models import Message, Conversation
    conversations = Conversation.objects.filter(patient=patient)
    unread_messages = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=patient).count()
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'doctors_available': doctors,
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'dashboard/patient_dashboard.html', context)

def admin_dashboard(request):
    """Admin dashboard"""
    from accounts.models import CustomUser
    
    total_users = CustomUser.objects.count()
    doctors = CustomUser.objects.filter(role='doctor').count()
    patients = CustomUser.objects.filter(role='patient').count()
    pending_doctors = DoctorProfile.objects.filter(is_approved=False).count()
    
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    
    context = {
        'total_users': total_users,
        'doctors': doctors,
        'patients': patients,
        'pending_doctors': pending_doctors,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)