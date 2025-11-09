from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PrescriptionTemplate


@login_required(login_url='login')
def get_template_items(request, template_id):
    """API endpoint to get prescription template items"""
    try:
        template = PrescriptionTemplate.objects.get(id=template_id, is_active=True)
        items = template.items.all().values(
            'medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions'
        )
        return JsonResponse({
            'status': 'success',
            'items': list(items)
        })
    except PrescriptionTemplate.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Template not found'
        }, status=404)
