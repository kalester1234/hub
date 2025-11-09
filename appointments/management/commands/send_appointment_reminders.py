from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from appointments.models import Appointment, AppointmentReminder
from datetime import timedelta


class Command(BaseCommand):
    help = 'Send appointment reminders to patients and doctors'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f'Starting reminder check at {now}')

        # Send 24-hour reminders
        self.send_reminders_for_timeframe(
            now + timedelta(hours=24),
            '24h',
            '24 Hours Before'
        )

        # Send 1-hour reminders
        self.send_reminders_for_timeframe(
            now + timedelta(hours=1),
            '1h',
            '1 Hour Before'
        )

        self.stdout.write('Reminder check completed.')

    def send_reminders_for_timeframe(self, target_time, reminder_type, description):
        """Send reminders for appointments around a specific time"""
        time_window_start = target_time - timedelta(minutes=30)
        time_window_end = target_time + timedelta(minutes=30)

        # Find confirmed appointments in the time window
        appointments = Appointment.objects.filter(
            appointment_date=target_time.date(),
            appointment_time__gte=time_window_start.time(),
            appointment_time__lte=time_window_end.time(),
            status='confirmed'
        ).select_related('doctor', 'patient')

        self.stdout.write(f'Found {appointments.count()} appointments for {description} reminders')

        for appointment in appointments:
            # Check if reminder already sent
            reminder, created = AppointmentReminder.objects.get_or_create(
                appointment=appointment,
                reminder_type=reminder_type,
                defaults={'is_sent': False}
            )

            if not reminder.is_sent:
                self.send_reminder_email(appointment, description)
                reminder.is_sent = True
                reminder.sent_at = timezone.now()
                reminder.save()
                self.stdout.write(f'Sent {description} reminder for appointment {appointment.id}')

    def send_reminder_email(self, appointment, reminder_type):
        """Send reminder email to patient and doctor"""
        subject = f'Appointment Reminder - {reminder_type}'

        patient_message = f"""
        Dear {appointment.patient.get_full_name()},

        This is a reminder for your upcoming appointment:

        Date: {appointment.appointment_date.strftime('%B %d, %Y')}
        Time: {appointment.appointment_time.strftime('%I:%M %p')}
        Doctor: Dr. {appointment.doctor.get_full_name()}
        Reason: {appointment.reason or 'Not specified'}

        Please arrive 15 minutes early for your appointment.

        Best regards,
        Medical Connect Team
        """

        doctor_message = f"""
        Dear Dr. {appointment.doctor.get_full_name()},

        This is a reminder for your upcoming appointment:

        Date: {appointment.appointment_date.strftime('%B %d, %Y')}
        Time: {appointment.appointment_time.strftime('%I:%M %p')}
        Patient: {appointment.patient.get_full_name()}
        Reason: {appointment.reason or 'Not specified'}

        Best regards,
        Medical Connect Team
        """

        try:
            # Send to patient
            send_mail(
                subject,
                patient_message,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.patient.email],
                fail_silently=False,
            )

            # Send to doctor
            send_mail(
                subject,
                doctor_message,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.doctor.email],
                fail_silently=False,
            )

            self.stdout.write(f'Successfully sent reminder emails for appointment {appointment.id}')

        except Exception as e:
            self.stderr.write(f'Failed to send reminder for appointment {appointment.id}: {str(e)}')
