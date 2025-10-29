#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import PatientProfile, DoctorProfile

User = get_user_model()

# Create test patient
if not User.objects.filter(username='patient@test.com').exists():
    patient = User.objects.create_user(
        username='patient@test.com',
        email='patient@test.com',
        password='patient123',
        first_name='John',
        last_name='Doe',
        phone='1234567890',
        role='patient'
    )
    PatientProfile.objects.create(
        user=patient,
        blood_type='O+'
    )
    print("✓ Test Patient created")
    print("  Username: patient@test.com")
    print("  Password: patient123")
else:
    print("Patient account already exists")

# Create test doctor
if not User.objects.filter(username='doctor@test.com').exists():
    doctor = User.objects.create_user(
        username='doctor@test.com',
        email='doctor@test.com',
        password='doctor123',
        first_name='Dr.',
        last_name='Smith',
        phone='9876543210',
        role='doctor'
    )
    DoctorProfile.objects.create(
        user=doctor,
        specialization='General Practice',
        license_number='MD123456',
        experience_years=5,
        consultation_fee=50.00,
        available_from='09:00',
        available_to='17:00',
        is_approved=True,
        rating=4.5
    )
    print("✓ Test Doctor created")
    print("  Username: doctor@test.com")
    print("  Password: doctor123")
else:
    print("Doctor account already exists")