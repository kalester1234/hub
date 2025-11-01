#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from datetime import time
from decimal import Decimal
from django.contrib.auth import get_user_model
from accounts.models import PatientProfile, DoctorProfile
from appointments.models import AvailabilitySlot

User = get_user_model()

def ensure_patient():
    user, created = User.objects.get_or_create(
        username='patient@test.com',
        defaults={
            'email': 'patient@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'role': 'patient',
        },
    )
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.email = 'patient@test.com'
    user.phone = '1234567890'
    user.role = 'patient'
    user.set_password('patient123')
    user.save()
    PatientProfile.objects.get_or_create(user=user, defaults={'blood_type': 'O+'})
    if created:
        print("✓ Test Patient created")
    else:
        print("Patient account refreshed")
    print("  Username: patient@test.com")
    print("  Password: patient123")


def ensure_doctors():
    doctor_definitions = [
        {
            'username': 'asha.patel@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Asha',
            'last_name': 'Patel',
            'phone': '555010001',
            'specialization': 'cardiology',
            'license_number': 'CARD-24-001',
            'experience_years': 14,
            'hospital_name': 'Summit Heart Institute',
            'consultation_fee': Decimal('220.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.9,
        },
        {
            'username': 'miguel.reyes@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Miguel',
            'last_name': 'Reyes',
            'phone': '555010002',
            'specialization': 'cardiology',
            'license_number': 'CARD-24-002',
            'experience_years': 11,
            'hospital_name': 'Summit Heart Institute',
            'consultation_fee': Decimal('210.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'lauren.chen@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Lauren',
            'last_name': 'Chen',
            'phone': '555010003',
            'specialization': 'cardiology',
            'license_number': 'CARD-24-003',
            'experience_years': 9,
            'hospital_name': 'Summit Heart Institute',
            'consultation_fee': Decimal('205.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.8,
        },
        {
            'username': 'priya.khanna@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Priya',
            'last_name': 'Khanna',
            'phone': '555020001',
            'specialization': 'dermatology',
            'license_number': 'DERM-24-001',
            'experience_years': 10,
            'hospital_name': 'Radiant Skin Center',
            'consultation_fee': Decimal('160.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.9,
        },
        {
            'username': 'aaron.brooks@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Aaron',
            'last_name': 'Brooks',
            'phone': '555020002',
            'specialization': 'dermatology',
            'license_number': 'DERM-24-002',
            'experience_years': 12,
            'hospital_name': 'Radiant Skin Center',
            'consultation_fee': Decimal('180.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.6,
        },
        {
            'username': 'elise.dubois@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Elise',
            'last_name': 'Dubois',
            'phone': '555020003',
            'specialization': 'dermatology',
            'license_number': 'DERM-24-003',
            'experience_years': 8,
            'hospital_name': 'Radiant Skin Center',
            'consultation_fee': Decimal('155.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.8,
        },
        {
            'username': 'kavita.menon@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Kavita',
            'last_name': 'Menon',
            'phone': '555030001',
            'specialization': 'neurology',
            'license_number': 'NEUR-24-001',
            'experience_years': 15,
            'hospital_name': 'NeuroCare Institute',
            'consultation_fee': Decimal('240.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.9,
        },
        {
            'username': 'daniel.harper@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Daniel',
            'last_name': 'Harper',
            'phone': '555030002',
            'specialization': 'neurology',
            'license_number': 'NEUR-24-002',
            'experience_years': 13,
            'hospital_name': 'NeuroCare Institute',
            'consultation_fee': Decimal('230.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'sofia.rinaldi@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Sofia',
            'last_name': 'Rinaldi',
            'phone': '555030003',
            'specialization': 'neurology',
            'license_number': 'NEUR-24-003',
            'experience_years': 9,
            'hospital_name': 'NeuroCare Institute',
            'consultation_fee': Decimal('225.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.8,
        },
        {
            'username': 'lily.evans@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Lily',
            'last_name': 'Evans',
            'phone': '555040001',
            'specialization': 'pediatrics',
            'license_number': 'PEDS-24-001',
            'experience_years': 11,
            'hospital_name': 'BrightStart Children\'s Hospital',
            'consultation_fee': Decimal('140.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.8,
        },
        {
            'username': 'omar.siddiqi@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Omar',
            'last_name': 'Siddiqi',
            'phone': '555040002',
            'specialization': 'pediatrics',
            'license_number': 'PEDS-24-002',
            'experience_years': 9,
            'hospital_name': 'BrightStart Children\'s Hospital',
            'consultation_fee': Decimal('135.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'hannah.morales@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Hannah',
            'last_name': 'Morales',
            'phone': '555040003',
            'specialization': 'pediatrics',
            'license_number': 'PEDS-24-003',
            'experience_years': 7,
            'hospital_name': 'BrightStart Children\'s Hospital',
            'consultation_fee': Decimal('130.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.6,
        },
        {
            'username': 'jason.wu@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Jason',
            'last_name': 'Wu',
            'phone': '555050001',
            'specialization': 'orthopedics',
            'license_number': 'ORTH-24-001',
            'experience_years': 13,
            'hospital_name': 'Flexion Orthopedic Center',
            'consultation_fee': Decimal('200.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.8,
        },
        {
            'username': 'emily.rhodes@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Emily',
            'last_name': 'Rhodes',
            'phone': '555050002',
            'specialization': 'orthopedics',
            'license_number': 'ORTH-24-002',
            'experience_years': 12,
            'hospital_name': 'Flexion Orthopedic Center',
            'consultation_fee': Decimal('210.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'naveen.iyer@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Naveen',
            'last_name': 'Iyer',
            'phone': '555050003',
            'specialization': 'orthopedics',
            'license_number': 'ORTH-24-003',
            'experience_years': 10,
            'hospital_name': 'Flexion Orthopedic Center',
            'consultation_fee': Decimal('205.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.7,
        },
        {
            'username': 'maria.gomez@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Maria',
            'last_name': 'Gomez',
            'phone': '555060001',
            'specialization': 'general',
            'license_number': 'GEN-24-001',
            'experience_years': 16,
            'hospital_name': 'Unity Family Clinic',
            'consultation_fee': Decimal('120.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.9,
        },
        {
            'username': 'caleb.foster@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Caleb',
            'last_name': 'Foster',
            'phone': '555060002',
            'specialization': 'general',
            'license_number': 'GEN-24-002',
            'experience_years': 12,
            'hospital_name': 'Unity Family Clinic',
            'consultation_fee': Decimal('110.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'zainab.ali@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Zainab',
            'last_name': 'Ali',
            'phone': '555060003',
            'specialization': 'general',
            'license_number': 'GEN-24-003',
            'experience_years': 8,
            'hospital_name': 'Unity Family Clinic',
            'consultation_fee': Decimal('105.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.6,
        },
        {
            'username': 'nisha.verma@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Nisha',
            'last_name': 'Verma',
            'phone': '555070001',
            'specialization': 'psychiatry',
            'license_number': 'PSY-24-001',
            'experience_years': 13,
            'hospital_name': 'Mindful Horizons Center',
            'consultation_fee': Decimal('180.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.8,
        },
        {
            'username': 'david.cho@demo.com',
            'password': 'Doctor123!',
            'first_name': 'David',
            'last_name': 'Cho',
            'phone': '555070002',
            'specialization': 'psychiatry',
            'license_number': 'PSY-24-002',
            'experience_years': 11,
            'hospital_name': 'Mindful Horizons Center',
            'consultation_fee': Decimal('175.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'amelia.grant@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Amelia',
            'last_name': 'Grant',
            'phone': '555070003',
            'specialization': 'psychiatry',
            'license_number': 'PSY-24-003',
            'experience_years': 9,
            'hospital_name': 'Mindful Horizons Center',
            'consultation_fee': Decimal('170.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.6,
        },
        {
            'username': 'noah.adams@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Noah',
            'last_name': 'Adams',
            'phone': '555080001',
            'specialization': 'other',
            'license_number': 'OTH-24-001',
            'experience_years': 10,
            'hospital_name': 'Global Care Center',
            'consultation_fee': Decimal('150.00'),
            'available_from': time(0, 0),
            'available_to': time(8, 0),
            'rating': 4.8,
        },
        {
            'username': 'sophia.mendez@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Sophia',
            'last_name': 'Mendez',
            'phone': '555080002',
            'specialization': 'other',
            'license_number': 'OTH-24-002',
            'experience_years': 12,
            'hospital_name': 'Global Care Center',
            'consultation_fee': Decimal('155.00'),
            'available_from': time(8, 0),
            'available_to': time(16, 0),
            'rating': 4.7,
        },
        {
            'username': 'liam.owens@demo.com',
            'password': 'Doctor123!',
            'first_name': 'Liam',
            'last_name': 'Owens',
            'phone': '555080003',
            'specialization': 'other',
            'license_number': 'OTH-24-003',
            'experience_years': 8,
            'hospital_name': 'Global Care Center',
            'consultation_fee': Decimal('145.00'),
            'available_from': time(16, 0),
            'available_to': time(23, 59),
            'rating': 4.6,
        },
    ]
    for entry in doctor_definitions:
        user, created = User.objects.get_or_create(
            username=entry['username'],
            defaults={
                'email': entry['username'],
                'first_name': entry['first_name'],
                'last_name': entry['last_name'],
                'phone': entry['phone'],
                'role': 'doctor',
            },
        )
        user.first_name = entry['first_name']
        user.last_name = entry['last_name']
        user.email = entry['username']
        user.phone = entry['phone']
        user.role = 'doctor'
        user.is_verified = True
        user.set_password(entry['password'])
        user.save()
        DoctorProfile.objects.update_or_create(
            user=user,
            defaults={
                'specialization': entry['specialization'],
                'license_number': entry['license_number'],
                'experience_years': entry['experience_years'],
                'hospital_name': entry['hospital_name'],
                'consultation_fee': entry['consultation_fee'],
                'available_from': entry['available_from'],
                'available_to': entry['available_to'],
                'is_approved': True,
                'rating': entry['rating'],
                'total_appointments': 0,
            },
        )
        status = 'created' if created else 'updated'
        print(f"✓ {entry['first_name']} {entry['last_name']} ({entry['username']}) {status}")


def ensure_availability_slots(slot_duration=30, break_count=2, break_duration=20):
    doctors = User.objects.filter(role='doctor', doctor_profile__isnull=False).select_related('doctor_profile')
    created = 0
    removed = 0
    for doctor in doctors:
        profile = doctor.doctor_profile
        start_minutes = profile.available_from.hour * 60 + profile.available_from.minute
        end_minutes = profile.available_to.hour * 60 + profile.available_to.minute
        if profile.available_to == time(23, 59):
            end_minutes = 24 * 60
        elif end_minutes <= start_minutes:
            end_minutes += 24 * 60
        shift_length = end_minutes - start_minutes
        if shift_length <= 0:
            continue
        total_break_minutes = break_count * break_duration
        effective_breaks = min(break_count, max((shift_length - break_duration) // break_duration, 0))
        if shift_length <= total_break_minutes:
            effective_breaks = 0
        break_intervals = []
        if effective_breaks:
            spacing = shift_length / (effective_breaks + 1)
            for index in range(1, effective_breaks + 1):
                tentative_start = start_minutes + int(round(spacing * index - break_duration / 2))
                lower_bound = start_minutes if not break_intervals else break_intervals[-1][1]
                upper_bound = end_minutes - (effective_breaks - index + 1) * break_duration
                if upper_bound < lower_bound:
                    upper_bound = lower_bound
                break_start = max(lower_bound, min(tentative_start, upper_bound))
                break_end = break_start + break_duration
                break_intervals.append((break_start, break_end))
        working_intervals = []
        cursor = start_minutes
        for break_start, break_end in break_intervals:
            if break_start > cursor:
                working_intervals.append((cursor, break_start))
            cursor = break_end
        if cursor < end_minutes:
            working_intervals.append((cursor, end_minutes))
        if not working_intervals:
            working_intervals.append((start_minutes, end_minutes))
        desired = set()
        for period_start, period_end in working_intervals:
            current = period_start
            while current < period_end:
                slot_end = min(current + slot_duration, period_end)
                slot_length = slot_end - current
                start_mod = current % (24 * 60)
                start_time = time(start_mod // 60, start_mod % 60)
                end_mod = slot_end % (24 * 60)
                end_time = time(end_mod // 60, end_mod % 60)
                for day in range(7):
                    _, was_created = AvailabilitySlot.objects.update_or_create(
                        doctor=doctor,
                        day_of_week=day,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'slot_duration': slot_length,
                            'is_active': True,
                        },
                    )
                    desired.add((day, start_time))
                    if was_created:
                        created += 1
                current = slot_end
        existing_slots = AvailabilitySlot.objects.filter(doctor=doctor)
        for slot in existing_slots:
            key = (slot.day_of_week, slot.start_time)
            if key not in desired:
                slot.delete()
                removed += 1
    print(f"✓ Availability slots ensured ({created} created, {removed} removed)")


def main():
    ensure_patient()
    ensure_doctors()
    ensure_availability_slots()


if __name__ == '__main__':
    main()
