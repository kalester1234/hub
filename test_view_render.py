import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.test import RequestFactory
from django.shortcuts import render
from appointments.views import browse_doctors

try:
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/appointments/browse/')

    # Call the view
    response = browse_doctors(request)
    print("View executed successfully")
    print(f"Response status: {response.status_code}")

except Exception as e:
    print(f"View error: {e}")
    import traceback
    traceback.print_exc()