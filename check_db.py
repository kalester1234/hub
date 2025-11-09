import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("PRAGMA table_info(accounts_doctorprofile)")
columns = cursor.fetchall()
print("Current columns in accounts_doctorprofile:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Check if total_appointments column exists
has_total_appointments = any(col[1] == 'total_appointments' for col in columns)
print(f"\nhas total_appointments column: {has_total_appointments}")

if not has_total_appointments:
    print("\nAdding total_appointments column...")
    cursor.execute("ALTER TABLE accounts_doctorprofile ADD COLUMN total_appointments integer NOT NULL DEFAULT 0")
    connection.commit()
    print("Column added successfully!")
