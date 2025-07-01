import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify

from .models import Service, Quote, QuoteItem, QuoteHistory, Notification

def home(request):
    """Home page view for all users"""
    context = {
        'title': 'Service Quotes Management System',
    }
    return render(request, 'home.html', context)

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Simple validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')
    
    return render(request, 'register.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('home')

def dashboard(request):
    """User dashboard"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Get user's quotes
    quotes = Quote.objects.filter(owner=request.user)
    
    # Get counts by status
    pending_count = quotes.filter(status='pending').count()
    accepted_count = quotes.filter(status='accepted').count()
    refused_count = quotes.filter(status='refused').count()
    
    # Get total value
    total_value = quotes.aggregate(total=Sum('total_amount'))['total'] or 0
    accepted_value = quotes.filter(status='accepted').aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get recent quotes
    recent_quotes = quotes.order_by('-created_at')[:5]
    
    # Get unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    context = {
        'quotes': quotes,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'refused_count': refused_count,
        'total_value': total_value,
        'accepted_value': accepted_value,
        'recent_quotes': recent_quotes,
        'notifications': notifications,
        'title': 'Dashboard',
    }
    
    return render(request, 'dashboard.html', context)

def quote_list(request):
    """List of user's quotes"""
    # Get filter parameters
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    # Base queryset
    quotes = Quote.objects.filter(owner=request.user)
    
    # Apply filters
    if status and status != 'all':
        quotes = quotes.filter(status=status)
    
    if search:
        quotes = quotes.filter(title__icontains=search) | quotes.filter(client_name__icontains=search)
    
    context = {
        'quotes': quotes,
        'status': status or 'all',
        'search': search or '',
        'title': 'My Quotes',
    }
    
    return render(request, 'quotes/list.html', context)

def quote_detail(request, slug):
    """Quote detail view"""
    quote = get_object_or_404(Quote, slug=slug, owner=request.user)
    items = quote.items.all()
    history = quote.history.all()
    
    context = {
        'quote': quote,
        'items': items,
        'history': history,
        'title': f'Quote: {quote.reference}',
    }
    
    return render(request, 'quotes/detail.html', context)

def quote_create(request):
    """Create a new quote"""
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        response_data = {'success': False, 'error': None, 'redirect': None}
        
        try:
            print("Received POST data:", request.POST)  # Debug log
            
            # Get form data
            title = request.POST.get('title')
            client_name = request.POST.get('client_name')
            client_email = request.POST.get('client_email')
            client_address = request.POST.get('client_address')
            description = request.POST.get('description')
            valid_until = request.POST.get('valid_until')
            items_data = request.POST.get('items')
            
            print("Items data:", items_data)  # Debug log
            
            # Validate required fields
            required_fields = {
                'title': title,
                'client_name': client_name,
                'client_email': client_email,
                'valid_until': valid_until
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                print(error_msg)  # Debug log
                if is_ajax:
                    response_data['error'] = error_msg
                    return JsonResponse(response_data, status=400)
                else:
                    messages.error(request, error_msg)
                    return render(request, 'quotes/create.html', {
                        'services': Service.objects.all(),
                        'title': 'Create Quote',
                        'form_data': request.POST
                    })
            
            # First create the quote without saving to generate reference
            quote = Quote(
                title=title,
                owner=request.user,
                client_name=client_name,
                client_email=client_email,
                client_address=client_address,
                description=description,
                valid_until=valid_until,
                total_amount=0  # Will be updated with items
            )
            
            # Generate reference and slug
            if not quote.reference:
                year = quote.created_at.strftime('%Y') if quote.created_at else '2025'
                quote.reference = f"DEV-{year}-{str(uuid.uuid4())[:8].upper()}"
            
            # Generate slug
            base_slug = slugify(quote.title)
            slug = base_slug
            num = 1
            while Quote.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            quote.slug = slug
            
            # Save the quote to get an ID
            quote.save()
            
            # Process items if any
            if items_data:
                try:
                    items = json.loads(items_data)
                    total_amount = 0
                    
                    for item in items:
                        service_id = item.get('service')
                        if not service_id:  # Skip if no service selected
                            continue
                            
                        quantity = float(item.get('quantity', 1))
                        price = float(item.get('price', 0))
                        item_total = quantity * price
                        
                        # Create the quote item - total_price is calculated automatically
                        quote_item = QuoteItem(
                            quote=quote,
                            service_id=service_id,
                            description=item.get('description', ''),
                            quantity=quantity,
                            unit_price=price
                        )
                        quote_item.save()  # This will trigger the total_price property
                        total_amount += float(quote_item.total_price)  # Use the calculated total_price
                    
                    # Update quote total
                    quote.total_amount = total_amount
                    quote.save()
                    
                except json.JSONDecodeError as e:
                    error_msg = 'There was an issue processing quote items. The quote was created but without items.'
                    print(f"{error_msg} Error: {e}")  # Debug log
                    if not is_ajax:
                        messages.warning(request, error_msg)
            
            # Create history entry
            QuoteHistory.objects.create(
                quote=quote,
                user=request.user,
                action="created",
                details="Quote was created"
            )
            
            # Prepare success response
            success_msg = f'Quote "{title}" created successfully.'
            if is_ajax:
                response_data.update({
                    'success': True,
                    'message': success_msg,
                    'redirect': reverse('quote_detail', kwargs={'slug': quote.slug})
                })
                return JsonResponse(response_data)
            else:
                messages.success(request, success_msg)
                return redirect('quote_detail', slug=quote.slug)
            
        except Exception as e:
            error_msg = f'An error occurred while creating the quote: {str(e)}'
            print(error_msg)  # Debug log
            
            if is_ajax:
                response_data['error'] = str(e)
                return JsonResponse(response_data, status=500)
            else:
                messages.error(request, error_msg)
                return render(request, 'quotes/create.html', {
                    'services': Service.objects.all(),
                    'title': 'Create Quote',
                    'form_data': request.POST
                })
    
    # Get services for form
    services = Service.objects.all()
    
    context = {
        'services': services,
        'title': 'Create Quote',
    }
    
    return render(request, 'quotes/create.html', context)

def quote_edit(request, slug):
    """Edit an existing quote"""
    quote = get_object_or_404(Quote, slug=slug, owner=request.user)
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        response_data = {'success': False, 'error': None, 'redirect': None}
        
        # Check if this is just a status update
        update_status_only = request.POST.get('update_status_only') == '1'
        
        try:
            # Get form data
            title = request.POST.get('title')
            client_name = request.POST.get('client_name')
            client_email = request.POST.get('client_email')
            client_address = request.POST.get('client_address')
            description = request.POST.get('description')
            valid_until = request.POST.get('valid_until')
            status = request.POST.get('status')
            
            # Get items data from form
            items_data = []
            item_services = request.POST.getlist('item_service')
            item_descriptions = request.POST.getlist('item_description')
            item_quantities = request.POST.getlist('item_quantity')
            item_prices = request.POST.getlist('item_price')
            
            # Convert to list of item dictionaries
            for i in range(len(item_services)):
                if item_services[i]:  # Only add if service is selected
                    items_data.append({
                        'service': item_services[i],
                        'description': item_descriptions[i] if i < len(item_descriptions) else '',
                        'quantity': item_quantities[i] if i < len(item_quantities) else 1,
                        'price': item_prices[i] if i < len(item_prices) else 0
                    })
            
            # Validate required fields
            required_fields = {}
            
            if not update_status_only:
                # Only require these fields for full quote updates
                required_fields.update({
                    'title': title,
                    'client_name': client_name,
                    'client_email': client_email,
                    'valid_until': valid_until,
                    'status': status
                })
            else:
                # Only require status for status-only updates
                required_fields = {'status': status}
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                if is_ajax:
                    response_data['error'] = error_msg
                    return JsonResponse(response_data, status=400)
                else:
                    messages.error(request, error_msg)
                    return render(request, 'quotes/edit.html', {
                        'quote': quote,
                        'services': Service.objects.all(),
                        'title': f'Edit Quote: {quote.reference}',
                        'form_data': request.POST
                    })
            
            # Update quote
            quote.title = title
            quote.client_name = client_name
            quote.client_email = client_email
            quote.client_address = client_address
            quote.description = description
            quote.valid_until = valid_until
            
            # Check if status changed
            status_changed = quote.status != status
            old_status = quote.status
            quote.status = status
            
            # Process items if any
            if items_data and not update_status_only:
                # Delete existing items
                quote.items.all().delete()
                total_amount = 0
                
                for item in items_data:
                    service_id = item.get('service')
                    if not service_id:  # Skip if no service selected
                        continue
                        
                    try:
                        quantity = float(item.get('quantity', 1))
                        price = float(item.get('price', 0))
                        
                        # Create the quote item - total_price is calculated automatically
                        quote_item = QuoteItem(
                            quote=quote,
                            service_id=service_id,
                            description=item.get('description', ''),
                            quantity=quantity,
                            unit_price=price
                        )
                        quote_item.save()  # This will trigger the total_price property
                        total_amount += float(quote_item.total_price)
                    except (ValueError, TypeError) as e:
                        print(f"Error processing item: {e}")
                        continue
                
                # Update quote total
                quote.total_amount = total_amount
            
            # Save the quote with updated fields
            quote.save()
            
            # Create appropriate history entry and notifications
            if update_status_only:
                # For status-only updates, always create a status change history
                QuoteHistory.objects.create(
                    quote=quote,
                    user=request.user,
                    action="status_changed",
                    details=f"Status changed from {old_status} to {status}"
                )
                
                Notification.objects.create(
                    user=request.user,
                    quote=quote,
                    message=f"Quote {quote.reference} status changed to {status}"
                )
            else:
                # For full updates, create a general update history
                QuoteHistory.objects.create(
                    quote=quote,
                    user=request.user,
                    action="updated",
                    details="Quote was updated"
                )
                
                # And if status changed, create an additional status change history
                if status_changed:
                    QuoteHistory.objects.create(
                        quote=quote,
                        user=request.user,
                        action="status_changed",
                        details=f"Status changed from {old_status} to {status}"
                    )
                    
                    Notification.objects.create(
                        user=request.user,
                        quote=quote,
                        message=f"Quote {quote.reference} status changed to {status}"
                    )
            
            # Prepare success response
            if update_status_only:
                success_msg = f'Quote status updated to {status}.'
            else:
                success_msg = f'Quote "{title}" updated successfully.'
                
            if is_ajax:
                response_data.update({
                    'success': True,
                    'message': success_msg,
                    'redirect': reverse('quote_detail', kwargs={'slug': quote.slug})
                })
                return JsonResponse(response_data)
            else:
                messages.success(request, success_msg)
                return redirect('quote_detail', slug=quote.slug)
            
        except Exception as e:
            error_msg = f'An error occurred while updating the quote: {str(e)}'
            print(error_msg)  # Debug log
            
            if is_ajax:
                response_data['error'] = str(e)
                return JsonResponse(response_data, status=500)
            else:
                messages.error(request, error_msg)
                return render(request, 'quotes/edit.html', {
                    'quote': quote,
                    'services': Service.objects.all(),
                    'title': f'Edit Quote: {quote.reference}',
                    'form_data': request.POST
                })
    
    # Get services for form
    services = Service.objects.all()
    
    context = {
        'quote': quote,
        'services': services,
        'title': f'Edit Quote: {quote.reference}',
    }
    
    return render(request, 'quotes/edit.html', context)

def profile(request):
    """User profile view"""
    if request.method == 'POST':
        # Update user profile
        user = request.user
        
        # Basic form processing
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'user': request.user,
        'title': 'My Profile',
    }
    
    return render(request, 'profile.html', context)

# Admin views
def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get counts
    total_quotes = Quote.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    total_services = Service.objects.count()
    
    # Get quotes by status
    pending_count = Quote.objects.filter(status='pending').count()
    accepted_count = Quote.objects.filter(status='accepted').count()
    refused_count = Quote.objects.filter(status='refused').count()
    
    # Get financial data
    total_value = Quote.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    accepted_value = Quote.objects.filter(status='accepted').aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get recent activity
    recent_history = QuoteHistory.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_quotes': total_quotes,
        'total_users': total_users,
        'total_services': total_services,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'refused_count': refused_count,
        'total_value': total_value,
        'accepted_value': accepted_value,
        'recent_history': recent_history,
        'title': 'Admin Dashboard',
    }
    
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_users(request):
    """Admin user management view"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'title': 'User Management',
    }
    
    return render(request, 'admin/users.html', context)

@user_passes_test(is_admin)
def admin_services(request):
    """Admin service management view"""
    services = Service.objects.all()
    
    if request.method == 'POST':
        # Handle service creation/update
        service_id = request.POST.get('service_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        unit_price = request.POST.get('unit_price')
        
        if service_id:  # Update existing service
            service = get_object_or_404(Service, id=service_id)
            service.name = name
            service.description = description
            service.unit_price = unit_price
            service.save()
            messages.success(request, f'Service "{name}" updated successfully.')
        else:  # Create new service
            Service.objects.create(
                name=name,
                description=description,
                unit_price=unit_price
            )
            messages.success(request, f'Service "{name}" created successfully.')
        
        return redirect('admin_services')
    
    context = {
        'services': services,
        'title': 'Service Management',
    }
    
    return render(request, 'admin/services.html', context)