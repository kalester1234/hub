from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from django.db.models import Q
from .models import Appointment, AvailabilitySlot, Prescription, DoctorLeave, PrescriptionItem, PrescriptionTemplate, PrescriptionTemplateItem

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields['appointment_date'].widget.attrs['min'] = today.isoformat()

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        if appointment_date:
            today = timezone.localdate()
            if appointment_date < today:
                self.add_error('appointment_date', 'You cannot select a past date.')
        if appointment_date and appointment_time:
            now = timezone.localtime()
            if appointment_date == now.date() and appointment_time <= now.time():
                self.add_error('appointment_time', 'Select a time in the future.')
        return cleaned_data


class AvailabilitySlotForm(forms.ModelForm):
    DAY_EVERYDAY = 'everyday'

    day_of_week = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = AvailabilitySlot
        fields = ['day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'slot_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_everyday = False
        day_choices = [(str(value), label) for value, label in AvailabilitySlot.DAYS_OF_WEEK]
        day_choices.append((self.DAY_EVERYDAY, 'Everyday'))
        self.fields['day_of_week'].choices = day_choices

    def clean_day_of_week(self):
        value = self.cleaned_data.get('day_of_week')
        if value == self.DAY_EVERYDAY:
            self.apply_everyday = True
            return AvailabilitySlot.DAYS_OF_WEEK[0][0]
        try:
            return int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError('Select a valid day.')

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
    template = forms.ModelChoiceField(
        queryset=PrescriptionTemplate.objects.filter(is_active=True),
        required=False,
        empty_label="Select a template (optional)",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Choose a prescription template to pre-fill medicines"
    )

    class Meta:
        model = Prescription
        fields = ['instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide overall guidance or precautions'})
        }

    def __init__(self, *args, **kwargs):
        doctor_profile = kwargs.pop('doctor_profile', None)
        super().__init__(*args, **kwargs)
        # Filter templates by doctor's specialization if doctor_profile is available
        if doctor_profile:
            self.fields['template'].queryset = PrescriptionTemplate.objects.filter(
                is_active=True
            ).filter(
                Q(specialization=doctor_profile.specialization) |
                Q(specialization__isnull=True) |
                Q(specialization='')
            )


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


class PrescriptionTemplateForm(forms.ModelForm):
    class Meta:
        model = PrescriptionTemplate
        fields = ['name', 'description', 'specialization', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


PrescriptionTemplateItemFormSet = inlineformset_factory(
    PrescriptionTemplate,
    PrescriptionTemplateItem,
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
