from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Admin can do anything
        if request.user.is_staff:
            return True
            
        # Check if object has an owner field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        # If the object is a QuoteItem, check the quote's owner
        if hasattr(obj, 'quote'):
            return obj.quote.owner == request.user
            
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        # If the object is a QuoteItem, check the quote's owner
        if hasattr(obj, 'quote'):
            return obj.quote.owner == request.user
            
        return False