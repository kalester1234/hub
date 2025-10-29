from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model
from .models import Appointment, AvailabilitySlot, Prescription
from .forms import AppointmentBookingForm, AvailabilitySlotForm, PrescriptionForm, AppointmentStatusForm
from accounts.models import DoctorProfile
from messaging.models import Notification, Conversation

CustomUser = get_user_model()

@login_required(login_url='login')
def browse_doctors(request):
    """Browse and search doctors"""
    specialization = request.GET.get('specialization', '')
    search = request.GET.get('search', '')
    
    doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
    
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    context = {
        'doctors': doctors,
        'specializations': DoctorProfile._meta.get_field('specialization').choices,
        'search': search,
        'specialization': specialization
    }
    return render(request, 'appointments/browse_doctors.html', context)

@login_required(login_url='login')
def doctor_detail(request, doctor_id):
    """View doctor profile and available slots"""
    doctor_profile = get_object_or_404(DoctorProfile, user_id=doctor_id, is_approved=True)
    doctor = doctor_profile.user
    
    # Get available slots for next 30 days
    today = timezone.now().date()
    available_dates = []
    
    for i in range(30):
        date = today + timedelta(days=i)
        day_of_week = date.weekday()
        
        # Check if doctor has availability for this day
        slots = AvailabilitySlot.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        
        if slots.exists():
            # Check if there are available appointments
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                status__in=['confirmed', 'pending']
            ).count()
            
            available_dates.append({
                'date': date,
                'appointments': existing_appointments,
                'slots_available': True
            })
    
    context = {
        'doctor': doctor,
        'doctor_profile': doctor_profile,
        'available_dates': available_dates
    }
    return render(request, 'appointments/doctor_detail.html', context)

@login_required(login_url='login')
def book_appointment(request, doctor_id):
    """Book appointment with doctor"""
    if request.user.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('browse_doctors')
    
    doctor = get_object_or_404(CustomUser, id=doctor_id, role='doctor')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            
            # Calculate end_time (default 30 minutes consultation)
            start_time = appointment.appointment_time
            end_datetime = datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)
            appointment.end_time = end_datetime.time()
            
            # Check if slot already exists
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                status__in=['confirmed', 'pending']
            ).exists()
            
            if existing:
                messages.error(request, 'This time slot is already booked.')
                return redirect('book_appointment', doctor_id=doctor_id)
            
            appointment.save()
            
            # Create notification for doctor
            Notification.objects.create(
                user=doctor,
                notification_type='appointment_request',
                title='New Appointment Request',
                description=f'{request.user.get_full_name()} has requested an appointment',
                related_appointment=appointment
            )
            
            messages.success(request, 'Appointment booked successfully! Awaiting confirmation.')
            return redirect('my_appointments')
    else:
        form = AppointmentBookingForm()
    
    context = {
        'form': form,
        'doctor': doctor
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required(login_url='login')
def my_appointments(request):
    """View user's appointments"""
    if request.user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=request.user)
    else:
        appointments = Appointment.objects.filter(patient=request.user)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
        'status_choices': Appointment._meta.get_field('status').choices,
        'current_status': status_filter
    }
    return render(request, 'appointments/my_appointments.html', context)

@login_required(login_url='login')
def appointment_detail(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('my_appointments')
    
    can_edit = (request.user == appointment.doctor) and (appointment.status == 'pending')
    
    if request.method == 'POST' and can_edit:
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            
            # Create notification
            notification_type = 'appointment_confirmed' if appointment.status == 'confirmed' else 'appointment_cancelled'
            Notification.objects.create(
                user=appointment.patient,
                notification_type=notification_type,
                title=f'Appointment {appointment.status.capitalize()}',
                description=f'Your appointment on {appointment.appointment_date} has been {appointment.status}',
                related_appointment=appointment
            )
            
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointment_detail', appointment_id=appointment.id)
    elif can_edit:
        form = AppointmentStatusForm(instance=appointment)
    else:
        form = None
    
    context = {
        'appointment': appointment,
        'form': form,
        'can_edit': can_edit
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required(login_url='login')
def manage_availability(request):
    """Manage doctor's availability slots"""
    if request.user.role != 'doctor':
        messages.error(request, 'Only doctors can manage availability.')
        return redirect('dashboard')
    
    slots = AvailabilitySlot.objects.filter(doctor=request.user)
    
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user
            slot.save()
            messages.success(request, 'Availability slot added successfully!')
            return redirect('manage_availability')
    else:
        form = AvailabilitySlotForm()
    
    context = {
        'form': form,
        'slots': slots
    }
    return render(request, 'appointments/manage_availability.html', context)

@login_required(login_url='login')
def add_prescription(request, appointment_id):
    """Add prescription to appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor:
        messages.error(request, 'Only the attending doctor can add prescriptions.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()
            messages.success(request, 'Prescription added successfully!')
            return redirect('appointment_detail', appointment_id=appointment.id)
    else:
        form = PrescriptionForm()
    
    context = {
        'form': form,
        'appointment': appointment
    }
    return render(request, 'appointments/add_prescription.html', context)

@login_required(login_url='login')
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('my_appointments')
    
    if appointment.status == 'cancelled':
        messages.warning(request, 'This appointment is already cancelled.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    # Notify the other party
    other_user = appointment.patient if request.user == appointment.doctor else appointment.doctor
    Notification.objects.create(
        user=other_user,
        notification_type='appointment_cancelled',
        title='Appointment Cancelled',
        description=f'The appointment on {appointment.appointment_date} has been cancelled',
        related_appointment=appointment
    )
    
    messages.success(request, 'Appointment cancelled successfully!')
    return redirect('my_appointments')