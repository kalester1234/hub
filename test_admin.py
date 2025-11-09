import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.test import RequestFactory
from accounts.admin import DoctorProfileAdmin
from accounts.models import DoctorProfile

# Create a mock request
factory = RequestFactory()
request = factory.get('/admin/accounts/doctorprofile/')

# Try to get the changelist
admin = DoctorProfileAdmin(DoctorProfile, None)
try:
    changelist = admin.get_changelist_instance(request)
    print("Admin changelist works")
except Exception as e:
    print(f"Admin error: {e}")
    import traceback
    traceback.print_exc()