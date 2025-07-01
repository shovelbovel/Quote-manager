from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Service(models.Model):
    """Model representing a service that can be included in quotes"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Quote(models.Model):
    """Model representing a quote (devis)"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    )
    
    title = models.CharField(max_length=255)
    reference = models.CharField(max_length=50, unique=True, editable=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes')
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField()
    client_address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Generate a unique reference if not set
        if not self.reference:
            year = self.created_at.strftime('%Y') if self.created_at else '2023'
            self.reference = f"DEV-{year}-{uuid.uuid4().hex[:6].upper()}"
        
        # Generate slug if not set or if duplicate exists
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Quote.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.title}"

class QuoteItem(models.Model):
    """Model representing an item in a quote"""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"{self.service.name} - {self.quote.reference}"

class QuoteHistory(models.Model):
    """Model for tracking changes made to quotes"""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)  # e.g., "created", "updated", "status_changed"
    details = models.TextField(blank=True)     # Details of what changed
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Quote histories'
    
    def __str__(self):
        return f"{self.action} on {self.quote.reference} by {self.user.username}"

class Notification(models.Model):
    """Model for notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."