from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Service, Quote, QuoteItem, Notification
from .serializers import ServiceSerializer, QuoteSerializer, QuoteItemSerializer, NotificationSerializer
from django.db import transaction

class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def list(self, request, *args, **kwargs):
        print("ServiceViewSet list called")  # Debug log
        print(f"Request user: {request.user}")  # Debug log
        print(f"Service count: {Service.objects.count()}")  # Debug log
        return super().list(request, *args, **kwargs)
    
    # Only require authentication for write operations
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

class QuoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer

class QuoteItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = QuoteItem.objects.all()
    serializer_class = QuoteItemSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and user.is_staff

@require_http_methods(['POST'])
@user_passes_test(is_admin)
@csrf_exempt  # Temporarily disable CSRF for testing - re-enable in production with proper CSRF handling
def toggle_user_active(request, user_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_active': user.is_active})
    return redirect('admin_users')

@require_http_methods(['POST'])
@user_passes_test(is_admin)
@csrf_exempt  # Temporarily disable CSRF for testing - re-enable in production with proper CSRF handling
def toggle_user_admin(request, user_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_staff': user.is_staff})
    return redirect('admin_users')

@require_http_methods(['POST'])
@user_passes_test(is_admin)
@csrf_exempt  # Temporarily disable CSRF for testing - re-enable in production with proper CSRF handling
def delete_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    user = get_object_or_404(User, id=user_id)
    user.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'User deleted'})
    return redirect('admin_users')

def admin_services(request):
    services = Service.objects.all()
    return render(request, 'admin/services.html', {'services': services})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    form = UserCreationForm(request.data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    form = PasswordChangeForm(user, request.data)
    if form.is_valid():
        form.save()
        return Response({'status': 'password changed'}, status=status.HTTP_200_OK)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    # Example: return some dummy stats
    data = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_services': Service.objects.count(),
        'total_quotes': Quote.objects.count(),
    }
    return Response(data)

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = 'is_active' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.save()
        from django.shortcuts import redirect
        return redirect('admin_services')
    return render(request, 'admin/edit_user.html', {'user': user})

def edit_user_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'admin/edit_user.html', {'user': user})

def create_service_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        unit_price = request.POST.get('unit_price', 0)
        
        try:
            unit_price = float(unit_price)
            if unit_price < 0:
                unit_price = 0
        except (ValueError, TypeError):
            unit_price = 0
            
        Service.objects.create(
            name=name,
            description=description,
            unit_price=unit_price
        )
        from django.shortcuts import redirect
        return redirect('admin_services')
    return render(request, 'admin/create_service.html')

def edit_service_page(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        
        # Update unit_price if provided
        unit_price = request.POST.get('unit_price')
        if unit_price is not None:
            try:
                unit_price = float(unit_price)
                if unit_price >= 0:  # Only update if it's a valid non-negative number
                    service.unit_price = unit_price
            except (ValueError, TypeError):
                pass  # Keep the existing unit_price if the input is invalid
                
        service.save()
        from django.shortcuts import redirect
        return redirect('admin_services')
    return render(request, 'admin/edit_service.html', {'service': service})

@require_http_methods(['POST'])
@user_passes_test(is_admin)
@csrf_exempt  # Temporarily disable CSRF for testing - re-enable in production with proper CSRF handling
def delete_service(request, service_id):
    """Delete a service"""
    if not request.user.is_authenticated or not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        return redirect('login')
    
    service = get_object_or_404(Service, id=service_id)
    service_name = service.name
    
    try:
        service.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'message': f'Service "{service_name}" has been deleted.'
            })
        
        messages.success(request, f'Service "{service_name}" has been deleted.')
        return redirect('admin_services')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error', 
                'message': f'Error deleting service: {str(e)}'
            }, status=500)
        
        messages.error(request, f'Error deleting service: {str(e)}')
        return redirect('admin_services')
    return redirect('admin_services')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_quote_total(request, pk):
    """
    API endpoint to update a quote's total amount.
    """
    try:
        quote = Quote.objects.get(pk=pk, owner=request.user)
        total_amount = float(request.data.get('total_amount', 0))
        
        with transaction.atomic():
            quote.total_amount = total_amount
            quote.save()
            
            # Create history entry
            QuoteHistory.objects.create(
                quote=quote,
                user=request.user,
                action="total_updated",
                details=f"Quote total updated to {total_amount}"
            )
            
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
    except Quote.DoesNotExist:
        return Response(
            {'status': 'error', 'message': 'Quote not found or access denied'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
