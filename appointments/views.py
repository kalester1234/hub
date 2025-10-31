from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta, time
from django.contrib.auth import get_user_model
import json
import re
from .models import Appointment, AvailabilitySlot, Prescription
from .forms import AppointmentBookingForm, AvailabilitySlotForm, PrescriptionForm, AppointmentStatusForm, PrescriptionItemFormSet
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
    appointment = get_object_or_404(
        Appointment.objects.select_related('doctor', 'patient').prefetch_related('prescription__items'),
        id=appointment_id
    )
    
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
    
    if appointment.status != 'completed':
        messages.error(request, 'Prescriptions can only be created after the consultation is completed.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    if hasattr(appointment, 'prescription'):
        messages.info(request, 'A prescription already exists for this consultation.')
        return redirect('edit_prescription', appointment_id=appointment.id)
    
    placeholder_prescription = Prescription(appointment=appointment)

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST, instance=placeholder_prescription, prefix='items')
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.last_modified_by = request.user
            prescription.save()
            formset.instance = prescription
            formset.save()
            messages.success(request, 'Prescription added successfully!')
            return redirect('appointment_detail', appointment_id=appointment.id)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet(instance=placeholder_prescription, prefix='items')
    
    context = {
        'form': form,
        'formset': formset,
        'appointment': appointment,
        'is_edit': False,
        'doctor_profile': getattr(request.user, 'doctor_profile', None)
    }
    return render(request, 'appointments/add_prescription.html', context)

@login_required(login_url='login')
def edit_prescription(request, appointment_id):
    """Edit an existing prescription"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor:
        messages.error(request, 'Only the attending doctor can edit prescriptions.')
        return redirect('my_appointments')
    
    if appointment.status != 'completed':
        messages.error(request, 'Prescriptions can only be updated after the consultation is completed.')
        return redirect('appointment_detail', appointment_id=appointment.id)
    
    prescription = getattr(appointment, 'prescription', None)
    if not prescription:
        messages.error(request, 'No prescription found for this consultation.')
        return redirect('add_prescription', appointment_id=appointment.id)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionItemFormSet(request.POST, instance=prescription, prefix='items')
        if form.is_valid() and formset.is_valid():
            updated_prescription = form.save(commit=False)
            updated_prescription.last_modified_by = request.user
            updated_prescription.save()
            formset.save()
            messages.success(request, 'Prescription updated successfully!')
            return redirect('appointment_detail', appointment_id=appointment.id)
    else:
        form = PrescriptionForm(instance=prescription)
        formset = PrescriptionItemFormSet(instance=prescription, prefix='items')
    
    context = {
        'form': form,
        'formset': formset,
        'appointment': appointment,
        'is_edit': True,
        'prescription': prescription,
        'doctor_profile': getattr(request.user, 'doctor_profile', None)
    }
    return render(request, 'appointments/add_prescription.html', context)


@login_required(login_url='login')
def download_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user != appointment.doctor and request.user != appointment.patient:
        messages.error(request, 'You do not have permission to download this prescription.')
        return redirect('my_appointments')

    prescription = getattr(appointment, 'prescription', None)
    if not prescription:
        messages.error(request, 'No prescription available for download.')
        return redirect('appointment_detail', appointment_id=appointment.id)

    items = list(prescription.items.all())
    if not items:
        messages.error(request, 'Prescription has no medicines to download yet.')
        return redirect('appointment_detail', appointment_id=appointment.id)

    updated_at = timezone.localtime(prescription.updated_at)
    created_at = timezone.localtime(prescription.created_at)
    doctor_name = f"Dr. {appointment.doctor.get_full_name()}"
    patient_name = appointment.patient.get_full_name()
    last_mod_by = prescription.last_modified_by.get_full_name() if prescription.last_modified_by else doctor_name

    lines = [
        f"Prescription Summary",
        f"Appointment ID: {appointment.id}",
        f"Patient: {patient_name}",
        f"Doctor: {doctor_name}",
        f"Consultation Date: {appointment.appointment_date.strftime('%b %d, %Y')}",
        f"Consultation Time: {appointment.appointment_time.strftime('%H:%M')}",
        "",
        "Medicines:",
    ]

    for index, item in enumerate(items, start=1):
        lines.extend([
            f"  {index}. {item.medicine_name}",
            f"     Dosage: {item.dosage or '—'}",
            f"     Frequency: {item.frequency or '—'}",
            f"     Duration (days): {item.duration_days if item.duration_days is not None else '—'}",
        ])
        if item.instructions:
            lines.append(f"     Instructions: {item.instructions}")
        lines.append("")

    if prescription.instructions:
        lines.extend([
            "General Instructions:",
            prescription.instructions,
            "",
        ])

    lines.extend([
        f"Created At: {created_at.strftime('%b %d, %Y %H:%M')}",
        f"Last Updated: {updated_at.strftime('%b %d, %Y %H:%M')} by {last_mod_by}",
    ])

    content = "\n".join(line for line in lines if line is not None)

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename=prescription_{appointment.id}.txt'
    return response


@login_required(login_url='login')
@require_POST
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user != appointment.doctor:
        messages.error(request, 'Only the attending doctor can update this consultation.')
        return redirect('appointment_detail', appointment_id=appointment.id)

    if appointment.status == 'completed':
        messages.info(request, 'This appointment is already marked as completed.')
        return redirect('appointment_detail', appointment_id=appointment.id)

    if appointment.status != 'confirmed':
        messages.warning(request, 'Only confirmed appointments can be marked as completed.')
        return redirect('appointment_detail', appointment_id=appointment.id)

    appointment.status = 'completed'
    appointment.save(update_fields=['status', 'updated_at'])

    Notification.objects.create(
        user=appointment.patient,
        notification_type='appointment_completed',
        title='Appointment Completed',
        description=f'Dr. {request.user.get_full_name()} has marked your appointment on {appointment.appointment_date} as completed.',
        related_appointment=appointment
    )

    messages.success(request, 'Appointment marked as completed.')

    next_url = request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)

    return redirect('appointment_detail', appointment_id=appointment.id)


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


def _parse_preferred_date(data, query, today):
    preferred_date = None
    date_str = data.get('preferred_date')
    if date_str:
        try:
            preferred_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            preferred_date = None
    if not preferred_date and query:
        if 'today' in query:
            preferred_date = today
        elif 'tomorrow' in query:
            preferred_date = today + timedelta(days=1)
        else:
            match = re.search(r'\d{4}-\d{2}-\d{2}', query)
            if match:
                try:
                    preferred_date = datetime.strptime(match.group(), '%Y-%m-%d').date()
                except ValueError:
                    preferred_date = None
        if not preferred_date:
            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for index, name in enumerate(weekdays):
                if name in query:
                    delta = (index - today.weekday()) % 7
                    if delta == 0:
                        delta = 7
                    preferred_date = today + timedelta(days=delta)
                    break
    return preferred_date


def _collect_available_slots(profiles, start_date, today):
    available_slots = []
    now_time = timezone.localtime().time()
    for profile in profiles:
        doctor = profile.user
        slots_qs = AvailabilitySlot.objects.filter(doctor=doctor, is_active=True)
        if not slots_qs.exists():
            continue
        for day_offset in range(0, 14):
            current_date = start_date + timedelta(days=day_offset)
            if current_date < today:
                continue
            day_slots = slots_qs.filter(day_of_week=current_date.weekday())
            if not day_slots.exists():
                continue
            existing_times = set(
                Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=current_date,
                    status__in=['pending', 'confirmed']
                ).values_list('appointment_time', flat=True)
            )
            for slot in day_slots:
                step = slot.slot_duration if slot.slot_duration else 30
                if step <= 0:
                    step = 30
                start_dt = datetime.combine(current_date, slot.start_time)
                end_dt = datetime.combine(current_date, slot.end_time)
                current_dt = start_dt
                while current_dt + timedelta(minutes=step) <= end_dt:
                    slot_time = current_dt.time()
                    if slot_time in existing_times:
                        current_dt += timedelta(minutes=step)
                        continue
                    if current_date == today and slot_time <= now_time:
                        current_dt += timedelta(minutes=step)
                        continue
                    available_slots.append({
                        'doctor': doctor,
                        'profile': profile,
                        'date': current_date,
                        'time': slot_time
                    })
                    if len(available_slots) >= 30:
                        return available_slots
                    current_dt += timedelta(minutes=step)
    return available_slots


@require_POST
def chatbot_suggest_slot(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, AttributeError):
        data = {}
    specialization = (data.get('specialization') or '').strip()
    query = (data.get('query') or '').lower().strip()
    today = timezone.localdate()
    preferred_date = _parse_preferred_date(data, query, today)
    start_date = preferred_date or today
    profiles = DoctorProfile.objects.filter(is_approved=True).select_related('user')
    if specialization and specialization != 'any':
        profiles = profiles.filter(specialization=specialization)
    specialization_map = dict(DoctorProfile.SPECIALIZATION_CHOICES)
    if not profiles.exists():
        message = "No doctors are available right now. Please try again soon."
        return JsonResponse({'status': 'empty', 'message': message, 'slots': []})
    available_slots = _collect_available_slots(profiles, start_date, today)
    if not available_slots:
        label = specialization_map.get(specialization, 'Doctors') if specialization else 'Doctors'
        message = f"No open slots found for {label.lower()} in the next two weeks. Please try a different specialty or time."
        return JsonResponse({'status': 'empty', 'message': message, 'slots': []})
    available_slots.sort(key=lambda item: (item['date'], item['time']))
    top_slots = available_slots[:3]
    slots_response = []
    for item in top_slots:
        doctor = item['doctor']
        profile = item['profile']
        date_value = item['date']
        time_value = item['time']
        slots_response.append({
            'doctor_id': doctor.id,
            'doctor_name': doctor.get_full_name() or doctor.username,
            'specialization': specialization_map.get(profile.specialization, 'Doctor'),
            'date': date_value.strftime('%Y-%m-%d'),
            'display_date': date_value.strftime('%b %d, %Y'),
            'time': time_value.strftime('%H:%M'),
            'display_time': time_value.strftime('%I:%M %p'),
            'location': profile.hospital_name or 'Clinic visit',
            'fee': str(profile.consultation_fee),
        })
    label = specialization_map.get(specialization, 'Doctors') if specialization else 'Doctors'
    if preferred_date:
        date_phrase = preferred_date.strftime('%b %d')
        message = f"Here are {label.lower()} available around {date_phrase}."
    else:
        message = f"Here are the next available {label.lower()} slots."
    return JsonResponse({'status': 'success', 'message': message, 'slots': slots_response})
