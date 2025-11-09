from django.contrib import admin
from .models import Appointment, AvailabilitySlot, Prescription, PrescriptionItem, PrescriptionTemplate, PrescriptionTemplateItem, DoctorLeave, AppointmentReminder

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['doctor__first_name', 'patient__first_name']
    date_hierarchy = 'appointment_date'

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_of_week_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'day_of_week']
    search_fields = ['doctor__first_name']

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0
    fields = ['medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'created_at']
    search_fields = ['appointment__patient__first_name']
    inlines = [PrescriptionItemInline]

class PrescriptionTemplateItemInline(admin.TabularInline):
    model = PrescriptionTemplateItem
    extra = 1
    fields = ['medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions']


@admin.register(PrescriptionTemplate)
class PrescriptionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'is_active', 'created_at']
    list_filter = ['is_active', 'specialization']
    search_fields = ['name', 'description']
    inlines = [PrescriptionTemplateItemInline]

@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'start_date']
    search_fields = ['doctor__first_name', 'doctor__last_name']
    date_hierarchy = 'start_date'

@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'sent_at', 'is_sent']
    list_filter = ['reminder_type', 'is_sent', 'sent_at']
    search_fields = ['appointment__patient__first_name', 'appointment__doctor__first_name']
