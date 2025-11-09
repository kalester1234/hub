#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_connect.settings")
django.setup()

from django.test import Client
from accounts.models import CustomUser
import traceback

# Create admin user
admin = CustomUser.objects.filter(role='admin').first()
if not admin:
    admin = CustomUser.objects.create_superuser('admin_test', 'admin@test.com', 'testpass123', role='admin')

client = Client()
client.force_login(admin)

try:
    print("Making request to /dashboard/admin/...")
    response = client.get('/dashboard/admin/')
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS - Response rendered")
    else:
        print(f"ERROR - Got status {response.status_code}")
        print(response.content.decode('utf-8', errors='ignore')[:500])
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
