import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from accounts.models import DoctorProfile

try:
    doctors = list(DoctorProfile.objects.all()[:1])
    print('Success: Found', len(doctors), 'doctors')
    if doctors:
        doctor = doctors[0]
        print('Doctor fields:', doctor.__dict__)
except Exception as e:
    print('Error:', e)