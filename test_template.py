import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_connect.settings')
django.setup()

from django.template.loader import get_template
from django.template import Context
from accounts.models import DoctorProfile

try:
    # Get the template
    template = get_template('appointments/browse_doctors.html')

    # Get doctors queryset
    doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')

    # Create context
    context = {
        'doctors': doctors,
        'specializations': DoctorProfile._meta.get_field('specialization').choices,
        'search': '',
        'specialization': ''
    }

    # Try to render
    html = template.render(context)
    print("Template rendered successfully")

except Exception as e:
    print(f"Template rendering error: {e}")
    import traceback
    traceback.print_exc()