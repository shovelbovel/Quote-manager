from django.http import JsonResponse
from .models import Service

def debug_services(request):
    services = list(Service.objects.all().values('id', 'name', 'unit_price', 'description'))
    return JsonResponse({
        'count': len(services),
        'services': services
    })
