import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from accounts.models import DoctorProfile

try:
    # Mimic the browse_doctors view
    doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
    print('Query successful, found', doctors.count(), 'doctors')

    # Try to iterate through them
    for doctor in doctors[:1]:
        print('Doctor:', doctor)
        print('Rating:', doctor.rating)
        print('Total appointments field:', doctor.total_appointments_field)

except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()