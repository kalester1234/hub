from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from collections import defaultdict
import json
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
        return redirect('admin_dashboard')
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

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard"""
    if request.user.role != 'admin':
        return redirect('dashboard')
    from accounts.models import CustomUser
    doctor_search_query = request.GET.get('doctor_search', '').strip()
    patient_search_query = request.GET.get('patient_search', '').strip()
    focus = request.GET.get('focus', '').strip()
    active_section = 'overview'
    manage_tab = 'doctors'
    users_tab = 'patients'
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_notifications_read':
            Notification.objects.filter(is_read=False).update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
            return redirect('admin_dashboard')
        if action == 'delete_patient':
            user_id = request.POST.get('user_id')
            patient = get_object_or_404(CustomUser, id=user_id, role='patient')
            patient.delete()
            messages.success(request, 'Patient removed successfully.')
            return redirect('admin_dashboard')
        if action == 'delete_doctor':
            user_id = request.POST.get('user_id')
            doctor = get_object_or_404(CustomUser, id=user_id, role='doctor')
            doctor.delete()
            messages.success(request, 'Doctor removed successfully.')
            return redirect('admin_dashboard')

    doctors_qs = CustomUser.objects.filter(role='doctor').select_related('doctor_profile')
    if doctor_search_query:
        doctors_qs = doctors_qs.filter(
            Q(first_name__icontains=doctor_search_query) |
            Q(last_name__icontains=doctor_search_query) |
            Q(username__icontains=doctor_search_query) |
            Q(email__icontains=doctor_search_query) |
            Q(phone__icontains=doctor_search_query) |
            Q(doctor_profile__hospital_name__icontains=doctor_search_query) |
            Q(doctor_profile__specialization__icontains=doctor_search_query)
        ).distinct()
        active_section = 'manage-data'
        manage_tab = 'doctors'
    patients_qs = CustomUser.objects.filter(role='patient').select_related('patient_profile')
    if patient_search_query:
        patients_qs = patients_qs.filter(
            Q(first_name__icontains=patient_search_query) |
            Q(last_name__icontains=patient_search_query) |
            Q(username__icontains=patient_search_query) |
            Q(email__icontains=patient_search_query) |
            Q(phone__icontains=patient_search_query) |
            Q(patient_profile__medical_history__icontains=patient_search_query)
        ).distinct()
        active_section = 'users'
        users_tab = 'patients'
    admin_qs = CustomUser.objects.filter(role='admin')
    total_users = CustomUser.objects.count()
    total_doctors = doctors_qs.count()
    total_patients = patients_qs.count()
    approved_doctors = DoctorProfile.objects.filter(is_approved=True).count()
    pending_doctors = DoctorProfile.objects.filter(is_approved=False).count()
    active_patients = patients_qs.filter(is_active=True).count()

    today = timezone.now().date()
    month_start = today.replace(day=1)
    upcoming_appointments = Appointment.objects.filter(appointment_date__gte=today).count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    completed_this_month = Appointment.objects.filter(
        status='completed',
        appointment_date__gte=month_start,
        appointment_date__lte=today
    ).count()

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
    status_palette = {
        'pending': '#F4B740',
        'confirmed': '#4C6EF5',
        'completed': '#0BA57A',
        'cancelled': '#EF4444'
    }
    chart_max = max([item['count'] for item in status_summary], default=0)
    chart_data = [
        {
            'value': item['value'],
            'label': item['label'],
            'count': item['count'],
            'height': int((item['count'] / chart_max) * 100) if chart_max else 0,
            'color': status_palette.get(item['value'], '#1B3A4B')
        }
        for item in status_summary
    ]
    has_chart_data = any(item['count'] for item in chart_data)

    hospital_profiles = list(
        DoctorProfile.objects.select_related('user')
        .exclude(hospital_name__isnull=True)
        .exclude(hospital_name__exact='')
        .order_by('hospital_name', 'user__first_name', 'user__last_name')
    )
    hospital_map = {}
    hospital_order = []
    for profile in hospital_profiles:
        hospital_name = profile.hospital_name.strip()
        if not hospital_name:
            continue
        key = hospital_name.casefold()
        if key not in hospital_map:
            hospital_map[key] = {
                'name': hospital_name,
                'doctors': 0,
                'emails': set(),
            }
            hospital_order.append(key)
        entry = hospital_map[key]
        entry['doctors'] += 1
        if profile.user.email:
            entry['emails'].add(profile.user.email)

    hospital_list_full = []
    for key in hospital_order:
        entry = hospital_map[key]
        hospital_list_full.append({
            'name': entry['name'],
            'count': entry['doctors'],
            'contact': ', '.join(sorted(entry['emails'])) if entry['emails'] else 'Not provided'
        })
    total_hospitals = len(hospital_list_full)
    hospital_list = hospital_list_full[:5]
    doctors_with_hospital = len(hospital_profiles)

    doctor_ids = list(doctors_qs.values_list('id', flat=True))
    doctor_records_map = defaultdict(list)
    doctor_records_total = defaultdict(int)
    if doctor_ids:
        current_time = timezone.localtime().time()
        doctor_appointments = Appointment.objects.filter(doctor_id__in=doctor_ids).filter(
            Q(appointment_date__lt=today) |
            Q(appointment_date=today, appointment_time__lte=current_time)
        ).select_related('patient').order_by('-appointment_date', '-appointment_time')
        for appointment in doctor_appointments:
            doctor_records_total[appointment.doctor_id] += 1
            if len(doctor_records_map[appointment.doctor_id]) < 5:
                doctor_records_map[appointment.doctor_id].append({
                    'patient': appointment.patient.get_full_name() or appointment.patient.username,
                    'date': appointment.appointment_date.strftime('%Y-%m-%d'),
                    'time': appointment.appointment_time.strftime('%H:%M'),
                    'status': appointment.get_status_display()
                })

    doctor_rows = []
    for doctor in doctors_qs.order_by('first_name', 'last_name'):
        profile = getattr(doctor, 'doctor_profile', None)
        records = doctor_records_map.get(doctor.id, [])
        doctor_rows.append({
            'id': doctor.id,
            'name': doctor.get_full_name() or doctor.username,
            'specialization': profile.get_specialization_display() if profile else 'Not specified',
            'hospital': profile.hospital_name if profile and profile.hospital_name else 'Not provided',
            'email': doctor.email or 'Not provided',
            'phone': doctor.phone or 'Not provided',
            'status': 'Approved' if profile and profile.is_approved else 'Pending',
            'status_class': 'approved' if profile and profile.is_approved else 'pending',
            'records_json': json.dumps(records),
            'records_total': doctor_records_total.get(doctor.id, 0)
        })

    patient_rows = []
    for patient in patients_qs.order_by('-date_joined'):
        profile = getattr(patient, 'patient_profile', None)
        patient_rows.append({
            'id': patient.id,
            'name': patient.get_full_name() or patient.username,
            'email': patient.email or 'Not provided',
            'phone': patient.phone or 'Not provided',
            'dob': profile.date_of_birth if profile and profile.date_of_birth else None,
            'joined': patient.date_joined,
            'status': 'Active' if patient.is_active else 'Inactive',
            'status_class': 'active' if patient.is_active else 'inactive'
        })

    admin_rows = []
    for admin_user in admin_qs.order_by('first_name', 'last_name'):
        admin_rows.append({
            'name': admin_user.get_full_name() or admin_user.username,
            'email': admin_user.email or 'Not provided',
            'phone': admin_user.phone or 'Not provided',
            'status': 'Active' if admin_user.is_active else 'Inactive',
            'status_class': 'active' if admin_user.is_active else 'inactive',
            'joined': admin_user.date_joined
        })

    appointments_recent = list(
        Appointment.objects.select_related('doctor', 'patient').order_by('-appointment_date', '-appointment_time')[:8]
    )
    appointments_pending_list = list(
        Appointment.objects.filter(status='pending').select_related('doctor', 'patient').order_by('appointment_date', 'appointment_time')[:8]
    )
    appointments_upcoming_list = list(
        Appointment.objects.filter(appointment_date__gte=today).select_related('doctor', 'patient').order_by('appointment_date', 'appointment_time')[:8]
    )

    notification_total = Notification.objects.count()
    notification_unread = Notification.objects.filter(is_read=False).count()
    notification_read = notification_total - notification_unread
    notifications_recent = list(
        Notification.objects.select_related('user').order_by('-created_at')[:10]
    )

    total_admins = admin_qs.count()

    doctor_metrics = {
        'total': total_doctors,
        'approved': approved_doctors,
        'pending': pending_doctors
    }
    hospital_metrics = {
        'total': total_hospitals,
        'with_doctors': doctors_with_hospital
    }
    user_metrics = {
        'patients_total': total_patients,
        'patients_active': active_patients,
        'patients_inactive': total_patients - active_patients,
        'admins_total': total_admins
    }
    appointment_counts = {
        'total': total_appointments,
        'pending': pending_appointments,
        'upcoming': upcoming_appointments,
        'completed': completed_appointments
    }
    notification_metrics = {
        'total': notification_total,
        'unread': notification_unread,
        'read': notification_read
    }

    def percentage(part, whole):
        return int((part / whole) * 100) if whole else 0

    stat_cards = [
        {
            'label': 'Total Doctors',
            'count': total_doctors,
            'icon': 'bi-people-fill',
            'accent': '#0BA57A',
            'progress': percentage(approved_doctors, total_doctors),
            'hint': f'{approved_doctors} approved'
        },
        {
            'label': 'Total Patients',
            'count': total_patients,
            'icon': 'bi-person-heart',
            'accent': '#36B37E',
            'progress': percentage(active_patients, total_patients),
            'hint': f'{active_patients} active'
        },
        {
            'label': 'Hospitals on Platform',
            'count': total_hospitals,
            'icon': 'bi-building',
            'accent': '#4C6EF5',
            'progress': percentage(doctors_with_hospital, total_doctors),
            'hint': 'Linked to doctor profiles'
        },
        {
            'label': 'Pending Approvals',
            'count': pending_doctors,
            'icon': 'bi-person-check',
            'accent': '#F4B740',
            'progress': percentage(pending_doctors, total_doctors),
            'hint': 'Awaiting review'
        },
    ]

    overview_cards = [
        {
            'label': 'Upcoming appointments',
            'value': upcoming_appointments,
            'icon': 'bi-calendar-event',
            'accent': '#0BA57A',
            'description': 'Scheduled from today onwards'
        },
        {
            'label': 'Pending appointments',
            'value': pending_appointments,
            'icon': 'bi-hourglass-split',
            'accent': '#F59E0B',
            'description': 'Awaiting confirmation'
        },
        {
            'label': 'Completed this month',
            'value': completed_this_month,
            'icon': 'bi-check2-circle',
            'accent': '#4C6EF5',
            'description': 'Month to date'
        },
    ]

    appointment_overview = {
        'total': total_appointments,
        'completed': completed_appointments,
        'completed_percent': percentage(completed_appointments, total_appointments),
        'pending': pending_appointments,
        'upcoming': upcoming_appointments,
    }

    user_name = request.user.get_full_name() or request.user.username
    user_summary = {
        'name': user_name,
        'role': request.user.get_role_display(),
        'status_text': f'{upcoming_appointments} upcoming appointments' if upcoming_appointments else 'No upcoming appointments scheduled',
        'notifications': request.user.notifications.filter(is_read=False).count(),
        'pending_doctors': pending_doctors,
        'initials': ''.join([part[0] for part in user_name.split()[:2]]).upper()
    }

    context = {
        'stat_cards': stat_cards,
        'hospital_headers': ['Hospital', 'Doctors', 'Primary Contact'],
        'hospital_list': hospital_list,
        'total_hospitals': total_hospitals,
        'chart_data': chart_data,
        'status_summary': status_summary,
        'appointment_overview': appointment_overview,
        'overview_cards': overview_cards,
        'user_summary': user_summary,
        'total_users': total_users,
        'pending_doctors': pending_doctors,
        'has_chart_data': has_chart_data,
        'doctor_rows': doctor_rows,
        'hospital_rows': hospital_list_full,
        'doctor_metrics': doctor_metrics,
        'hospital_metrics': hospital_metrics,
        'patient_rows': patient_rows,
        'admin_rows': admin_rows,
        'user_metrics': user_metrics,
        'appointments_recent': appointments_recent,
        'appointments_pending_list': appointments_pending_list,
        'appointments_upcoming_list': appointments_upcoming_list,
        'appointment_counts': appointment_counts,
        'notifications_recent': notifications_recent,
        'notification_metrics': notification_metrics,
        'doctor_search_query': doctor_search_query,
        'patient_search_query': patient_search_query,
        'active_section': focus or active_section,
        'manage_tab': manage_tab,
        'users_tab': users_tab,
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
        return redirect('admin_dashboard')
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
    return redirect('admin_dashboard')
