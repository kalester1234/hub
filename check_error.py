#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_connect.settings")
django.setup()

from dashboard.views import admin_dashboard
from django.test import RequestFactory
from accounts.models import CustomUser

factory = RequestFactory()

# Create an admin user
admin = CustomUser.objects.filter(role='admin').first()
if not admin:
    admin = CustomUser.objects.create_superuser('admin_test', 'admin@test.com', 'testpass123', role='admin')

# Create request
request = factory.get('/dashboard/admin/')
request.user = admin

try:
    print("Calling admin_dashboard()...")
    result = admin_dashboard(request)
    print(f"Success! Status: {result.status_code}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
