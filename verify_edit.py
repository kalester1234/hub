with open('dashboard/views.py') as f:
    content = f.read()
    
if 'appointment_count' in content:
    print("OK: File contains 'appointment_count'")
else:
    print("ERROR: File does NOT contain 'appointment_count'")
    
if 'total_appointments=Count' in content:
    print("ERROR: File still contains 'total_appointments=Count' annotation")
else:
    print("OK: File does NOT contain 'total_appointments=Count' annotation")
