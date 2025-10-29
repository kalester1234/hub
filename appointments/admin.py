from django.contrib import admin
from .models import Appointment, AvailabilitySlot, Prescription

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

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'medicine_name', 'dosage', 'frequency']
    search_fields = ['medicine_name']