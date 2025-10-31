from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from appointments.models import Appointment, AvailabilitySlot, DoctorLeave
from appointments.forms import AvailabilitySlotForm, DoctorLeaveForm
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
    doctor = request.user
    today = timezone.now().date()
    upcoming_qs = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today
    ).select_related('patient').prefetch_related('prescription__items').order_by('appointment_date', 'appointment_time')[:10]
    upcoming_appointments = list(upcoming_qs)
    for appointment in upcoming_appointments:
        appointment.has_prescription = hasattr(appointment, 'prescription')
    next_day_date = today + timedelta(days=1)
    next_day_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=next_day_date,
        status='confirmed'
    ).count()
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
    now = timezone.localtime()
    consultations_qs = Appointment.objects.filter(doctor=doctor).filter(
        Q(appointment_date__lt=today) |
        Q(appointment_date=today, appointment_time__lte=now.time())
    ).exclude(status='cancelled').select_related('patient').prefetch_related('prescription__items')
    recent_consultations = list(consultations_qs.order_by('-appointment_date', '-appointment_time')[:10])
    for consultation in recent_consultations:
        consultation.has_prescription = hasattr(consultation, 'prescription')
    pending_prescriptions = consultations_qs.filter(status='completed', prescription__isnull=True).count()
    availability_form = AvailabilitySlotForm()
    leave_form = DoctorLeaveForm()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'availability':
            availability_form = AvailabilitySlotForm(request.POST)
            if availability_form.is_valid():
                slot = availability_form.save(commit=False)
                slot.doctor = doctor
                try:
                    slot.save()
                    messages.success(request, 'Availability slot added successfully.')
                    return redirect('dashboard')
                except IntegrityError:
                    availability_form.add_error(None, 'This availability slot already exists.')
        elif form_type == 'leave':
            leave_form = DoctorLeaveForm(request.POST)
            if leave_form.is_valid():
                leave = leave_form.save(commit=False)
                leave.doctor = doctor
                leave.save()
                messages.success(request, 'Leave request submitted successfully.')
                return redirect('dashboard')
    availability_slots = AvailabilitySlot.objects.filter(doctor=doctor).order_by('day_of_week', 'start_time')
    leave_requests = DoctorLeave.objects.filter(doctor=doctor).order_by('-start_date')[:5]
    doctor_profile = getattr(doctor, 'doctor_profile', None)
    from messaging.models import Message, Conversation
    conversations = Conversation.objects.filter(doctor=doctor)
    unread_messages = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=doctor).count()
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    context = {
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'pending_requests': pending_requests,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'next_day_appointments': next_day_appointments,
        'pending_prescriptions': pending_prescriptions,
        'recent_consultations': recent_consultations,
        'unread_notifications': unread_notifications,
        'unread_messages': unread_messages,
        'availability_form': availability_form,
        'availability_slots': availability_slots,
        'leave_form': leave_form,
        'leave_requests': leave_requests,
        'doctor_profile': doctor_profile,
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
    status_counts = Appointment.objects.values('status').annotate(total=Count('id'))
    status_totals = {item['status']: item['total'] for item in status_counts}
    status_summary = [
        {
            'value': value,
            'label': label,
            'count': status_totals.get(value, 0)
        }
        for value, label in Appointment.STATUS_CHOICES
    ]
    recent_appointments = Appointment.objects.select_related('doctor', 'patient').order_by('-updated_at')[:10]
    
    context = {
        'total_users': total_users,
        'doctors': doctors,
        'patients': patients,
        'pending_doctors': pending_doctors,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'status_summary': status_summary,
        'status_choices': Appointment._meta.get_field('status').choices,
        'recent_appointments': recent_appointments,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required(login_url='login')
@require_POST
def admin_update_appointment_status(request, appointment_id):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard')
    appointment = get_object_or_404(Appointment, id=appointment_id)
    status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    valid_statuses = {value for value, _ in Appointment.STATUS_CHOICES}
    if status not in valid_statuses:
        messages.error(request, 'Invalid status selected.')
        return redirect('dashboard')
    appointment.status = status
    appointment.notes = notes
    appointment.save()
    notification_type = None
    if status == 'confirmed':
        notification_type = 'appointment_confirmed'
    elif status == 'cancelled':
        notification_type = 'appointment_cancelled'
    if notification_type:
        Notification.objects.create(
            user=appointment.patient,
            notification_type=notification_type,
            title=f'Appointment {status.capitalize()}',
            description=f'Your appointment on {appointment.appointment_date} with Dr. {appointment.doctor.get_full_name()} is now {status}.',
            related_appointment=appointment
        )
        Notification.objects.create(
            user=appointment.doctor,
            notification_type=notification_type,
            title=f'Appointment {status.capitalize()}',
            description=f'Appointment with {appointment.patient.get_full_name()} on {appointment.appointment_date} is now {status}.',
            related_appointment=appointment
        )
    messages.success(request, 'Appointment status updated successfully.')
    return redirect('dashboard')
