from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message, Notification
from .forms import MessageForm
from appointments.models import Appointment

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
    
    # Check permission
    if request.user != conversation.doctor and request.user != conversation.patient:
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('conversations_list')
    
    # Mark messages as read
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
            
            # Notify recipient
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
    
    messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'form': form
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
    
    context = {
        'notifications': notifications
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