from django.contrib import admin
from .models import Service, Quote, QuoteItem, QuoteHistory, Notification

class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1

class QuoteHistoryInline(admin.TabularInline):
    model = QuoteHistory
    extra = 0
    readonly_fields = ('user', 'action', 'details', 'created_at')
    can_delete = False
    max_num = 0

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('reference', 'title', 'owner', 'client_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reference', 'title', 'client_name', 'client_email')
    readonly_fields = ('reference', 'slug')
    inlines = [QuoteItemInline, QuoteHistoryInline]
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price', 'created_at')
    search_fields = ('name', 'description')

@admin.register(QuoteHistory)
class QuoteHistoryAdmin(admin.ModelAdmin):
    list_display = ('quote', 'user', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('quote__reference', 'user__username', 'details')
    readonly_fields = ('quote', 'user', 'action', 'details', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')