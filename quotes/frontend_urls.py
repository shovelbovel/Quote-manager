from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from . import frontend_views

urlpatterns = [
    # Public pages
    path('', frontend_views.home, name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('login/', frontend_views.login_view, name='login'),
    path('register/', frontend_views.register_view, name='register'),
    path('logout/', frontend_views.logout_view, name='logout'),
    
    # Authenticated user pages
    path('dashboard/', login_required(frontend_views.dashboard), name='dashboard'),
    path('quotes/', login_required(frontend_views.quote_list), name='quote_list'),
    path('quotes/create/', login_required(frontend_views.quote_create), name='quote_create'),
    path('quotes/<slug:slug>/', login_required(frontend_views.quote_detail), name='quote_detail'),
    path('quotes/<slug:slug>/edit/', login_required(frontend_views.quote_edit), name='quote_edit'),
    path('profile/', login_required(frontend_views.profile), name='profile'),
    
    # Admin pages
    path('admin-dashboard/', login_required(frontend_views.admin_dashboard), name='admin_dashboard'),
    path('manage/users/', frontend_views.admin_users, name='admin_users'),
    path('manage/services/', frontend_views.admin_services, name='admin_services'),
]