from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .debug_services import debug_services

# API Router
api_router = DefaultRouter()
api_router.register(r'services', views.ServiceViewSet)
api_router.register(r'quotes', views.QuoteViewSet, basename='quote')
api_router.register(r'quote-items', views.QuoteItemViewSet, basename='quoteitem')
api_router.register(r'notifications', views.NotificationViewSet, basename='notification')

# Admin URLs
admin_urls = [
    path('admin-stats/', views.admin_dashboard_stats, name='admin-stats'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit-user'),
    path('users/<int:user_id>/edit-page/', views.edit_user_page, name='edit-user-page'),
    path('users/create/', views.create_service_page, name='create-user-page'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle-user-active'),
    path('users/<int:user_id>/toggle-admin/', views.toggle_user_admin, name='toggle-user-admin'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
    path('services/', views.admin_services, name='admin_services'),
    path('services/create/', views.create_service_page, name='create-service-page'),
    path('services/<int:service_id>/edit/', views.edit_service_page, name='edit-service-page'),
    path('services/<int:service_id>/delete/', views.delete_service, name='delete-service'),
]

# API URLs
api_urls = [
    path('api/', include(api_router.urls)),
    path('api/register/', views.register_user, name='register'),
    path('api/change-password/', views.change_password, name='change-password'),
    path('api/quotes/<int:pk>/update_total/', views.update_quote_total, name='update_quote_total'),
    path('api/debug/services/', debug_services, name='debug_services'),
]

urlpatterns = api_urls + admin_urls
