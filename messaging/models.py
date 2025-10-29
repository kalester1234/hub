from django.db import models
from django.contrib.auth import get_user_model
from appointments.models import Appointment

CustomUser = get_user_model()

class Conversation(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='conversations_as_doctor')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='conversations_as_patient')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='conversation', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['doctor', 'patient']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: Dr. {self.doctor.get_full_name()} - {self.patient.get_full_name()}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('appointment_request', 'Appointment Request'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('message', 'New Message'),
        ('doctor_approved', 'Doctor Approved'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_read = models.BooleanField(default=False)
    related_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.user.get_full_name()}"