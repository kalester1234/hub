#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@medicalconnect.com',
        password='admin123456',
        role='admin'
    )
    print(f"✓ Superuser 'admin' created successfully")
else:
    print("Admin user already exists")