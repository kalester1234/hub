from django import forms
from django.forms import inlineformset_factory
from .models import Appointment, AvailabilitySlot, Prescription, DoctorLeave, PrescriptionItem

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please describe your symptoms or reason for visit'
            }),
        }


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_active']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'slot_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        slot_duration = cleaned_data.get('slot_duration')
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'End time must be after start time.')
        if slot_duration and slot_duration <= 0:
            self.add_error('slot_duration', 'Slot duration must be positive.')
        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide overall guidance or precautions'})
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    fields=['medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
    widgets={
        'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
        'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
        'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Twice a day'}),
        'duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
        'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Directions for this medicine'}),
    }
)


class DoctorLeaveForm(forms.ModelForm):
    class Meta:
        model = DoctorLeave
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share details for your leave request'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date cannot be before start date.')
        return cleaned_data


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }