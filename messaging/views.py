from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta
import requests
from .models import Conversation, Message, Notification
from .forms import MessageForm
from appointments.models import Appointment, AvailabilitySlot

def generate_llm_reply(prompt):
    try:
        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "phi3:mini", "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except requests.RequestException:
        return ""

@login_required(login_url='login')
def conversations_list(request):
    """List all conversations for the user"""
    if request.user.role == 'doctor':
        conversations = Conversation.objects.filter(doctor=request.user)
    else:
        conversations = Conversation.objects.filter(patient=request.user)
    
    unread_count = Message.objects.filter(
        conversation__in=conversations,
        is_read=False
    ).exclude(sender=request.user).count()
    
    context = {
        'conversations': conversations,
        'unread_count': unread_count
    }
    return render(request, 'messaging/conversations_list.html', context)

@login_required(login_url='login')
def conversation_detail(request, conversation_id):
    """View conversation messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user != conversation.doctor and request.user != conversation.patient:
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('conversations_list')
    
    doctor = conversation.doctor
    patient = conversation.patient
    is_patient_view = request.user == patient
    doctor_profile = getattr(doctor, 'doctor_profile', None)
    specialization = doctor_profile.get_specialization_display() if doctor_profile and hasattr(doctor_profile, 'get_specialization_display') else ''
    partner_name = patient.get_full_name() if request.user == doctor else f"Dr. {doctor.get_full_name()}"
    partner_meta = 'Patient' if request.user == doctor else (specialization or 'Doctor')
    def build_initials(name):
        parts = [part for part in name.split(' ') if part]
        if not parts:
            return '?'
        return ''.join(part[0] for part in parts[:2]).upper()
    partner_initials = build_initials(partner_name)
    booking_url = reverse('book_appointment', args=[doctor.id]) if is_patient_view else None
    def build_slot_suggestions(prefill_as_patient):
        slot_qs = AvailabilitySlot.objects.filter(doctor=doctor, is_active=True).order_by('day_of_week', 'start_time')
        slot_list = list(slot_qs)
        if not slot_list:
            return []
        now_local = timezone.localtime()
        start_date = now_local.date()
        window_days = 7
        max_items = 5
        end_date = start_date + timedelta(days=window_days - 1)
        existing_qs = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=start_date,
            appointment_date__lte=end_date,
            status__in=['pending', 'confirmed']
        ).values('appointment_date', 'appointment_time')
        taken_map = {}
        for item in existing_qs:
            date_key = item['appointment_date']
            time_value = item['appointment_time']
            taken_map.setdefault(date_key, set()).add(time_value)
        slots_by_day = {}
        for slot in slot_list:
            slots_by_day.setdefault(slot.day_of_week, []).append(slot)
        suggestions = []
        for offset in range(window_days):
            target_date = start_date + timedelta(days=offset)
            day_slots = slots_by_day.get(target_date.weekday(), [])
            if not day_slots:
                continue
            taken = taken_map.get(target_date, set())
            for slot in day_slots:
                duration = slot.slot_duration if slot.slot_duration and slot.slot_duration > 0 else 30
                cursor = datetime.combine(target_date, slot.start_time)
                slot_end = datetime.combine(target_date, slot.end_time)
                while cursor < slot_end:
                    end_cursor = cursor + timedelta(minutes=duration)
                    if end_cursor > slot_end:
                        break
                    if offset == 0 and cursor.time() <= now_local.time():
                        cursor = end_cursor
                        continue
                    if cursor.time() not in taken:
                        label = cursor.strftime('%a, %b %d • %I:%M %p')
                        if prefill_as_patient:
                            message_text = f"I would like to book an appointment on {cursor.strftime('%A, %B %d at %I:%M %p')} with you. Waiting for confirmation."
                        else:
                            message_text = f"I can offer {cursor.strftime('%A, %B %d at %I:%M %p')} for your visit."
                        suggestions.append({
                            'label': label,
                            'message': message_text,
                        })
                        if len(suggestions) >= max_items:
                            return suggestions
                    cursor = end_cursor
        return suggestions
    appointment_suggestions = build_slot_suggestions(is_patient_view)
    assistant_topics = [
        {
            'label': 'Medical Check-up',
            'message': 'I would like to schedule a medical check-up.'
        },
        {
            'label': 'Consultation',
            'message': 'I need a detailed consultation about my condition.'
        },
        {
            'label': 'Follow-up',
            'message': 'I want to arrange a follow-up visit.'
        },
        {
            'label': 'Other',
            'message': 'I have a different request regarding appointments.'
        },
    ]
    if is_patient_view:
        quick_replies = [
            {
                'label': 'Show available slots',
                'message': 'Could you share the available appointment slots this week?'
            },
            {
                'label': 'Prefer mornings',
                'message': 'Do you have any morning availability?'
            },
            {
                'label': 'Need online visit',
                'message': 'Can we switch to an online consultation?'
            },
        ]
        assistant_intro = f"I can help you coordinate the next visit with Dr. {doctor.get_full_name()}."
    else:
        quick_replies = [
            {
                'label': 'Share next openings',
                'message': 'Here are the next available times I can offer.'
            },
            {
                'label': 'Request more details',
                'message': 'Could you share a bit more about your current symptoms?'
            },
        ]
        assistant_intro = f"Coordinate the next steps for {patient.get_full_name()}."
    
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            if request.user == conversation.patient:
                assistant_text = generate_llm_reply(message.content)
                if assistant_text:
                    Message.objects.create(
                        conversation=conversation,
                        sender=conversation.doctor,
                        content=assistant_text,
                        is_read=False
                    )
            recipient = conversation.patient if request.user == conversation.doctor else conversation.doctor
            Notification.objects.create(
                user=recipient,
                notification_type='message',
                title='New Message',
                description=f'{request.user.get_full_name()} sent you a message',
            )
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    messages = conversation.messages.order_by('created_at')
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'appointment_suggestions': appointment_suggestions,
        'assistant_topics': assistant_topics,
        'quick_replies': quick_replies,
        'assistant_intro': assistant_intro,
        'booking_url': booking_url,
        'partner_name': partner_name,
        'partner_meta': partner_meta,
        'partner_initials': partner_initials,
        'is_patient_view': is_patient_view,
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required(login_url='login')
def start_conversation(request, user_id):
    """Start a conversation with a user"""
    try:
        other_user = get_object_or_404(request.user.__class__, id=user_id)
    except:
        messages.error(request, 'User not found.')
        return redirect('dashboard')
    
    if request.user == other_user:
        messages.error(request, 'You cannot start a conversation with yourself.')
        return redirect('dashboard')
    
    # Create or get conversation
    if request.user.role == 'doctor':
        conversation, created = Conversation.objects.get_or_create(
            doctor=request.user,
            patient=other_user
        )
    else:
        conversation, created = Conversation.objects.get_or_create(
            doctor=other_user,
            patient=request.user
        )
    
    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required(login_url='login')
def notifications(request):
    """View all notifications"""
    notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark as read if requested
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            notifications.filter(is_read=False).update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
            return redirect('notifications')
    
    has_unread_notifications = notifications.filter(is_read=False).exists()
    context = {
        'notifications': notifications,
        'has_unread_notifications': has_unread_notifications
    }
    return render(request, 'messaging/notifications.html', context)

@login_required(login_url='login')
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(request.user.notifications, id=notification_id)
    notification.is_read = True
    notification.save()
    
    if notification.related_appointment:
        return redirect('appointment_detail', appointment_id=notification.related_appointment.id)
    
    return redirect('notifications')