import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check for indexes
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='accounts_doctorprofile'")
    indexes = cursor.fetchall()
    print("Indexes on accounts_doctorprofile:")
    for idx in indexes:
        print(f"  {idx[0]}: {idx[1]}")

    # Check for triggers
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='accounts_doctorprofile'")
    triggers = cursor.fetchall()
    print("\nTriggers on accounts_doctorprofile:")
    for trig in triggers:
        print(f"  {trig[0]}: {trig[1]}")

    # Check foreign keys
    cursor.execute("PRAGMA foreign_key_list(accounts_doctorprofile)")
    fks = cursor.fetchall()
    print("\nForeign keys:")
    for fk in fks:
        print(f"  {fk}")