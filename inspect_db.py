import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.db import connection

# Inspect the accounts_doctorprofile table
with connection.cursor() as cursor:
    # Get table info
    cursor.execute("PRAGMA table_info(accounts_doctorprofile)")
    columns = cursor.fetchall()
    print("Columns in accounts_doctorprofile:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")

    # Check if total_appointments exists
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts_doctorprofile'")
    create_statement = cursor.fetchone()
    print("\nCreate statement:")
    print(create_statement[0])