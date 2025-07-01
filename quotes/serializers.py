from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Service, Quote, QuoteItem, QuoteHistory, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class QuoteItemSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = QuoteItem
        fields = ['id', 'service', 'service_name', 'description', 'quantity', 
                 'unit_price', 'total_price', 'created_at']

class QuoteSerializer(serializers.ModelSerializer):
    items = QuoteItemSerializer(many=True, read_only=True)
    owner_name = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Quote
        fields = ['id', 'reference', 'slug', 'title', 'owner', 'owner_name', 
                 'client_name', 'client_email', 'client_address', 'description', 
                 'status', 'total_amount', 'valid_until', 'items', 
                 'created_at', 'updated_at']
        read_only_fields = ['reference', 'slug']

class QuoteDetailSerializer(QuoteSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta(QuoteSerializer.Meta):
        pass

class QuoteHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = QuoteHistory
        fields = ['id', 'quote', 'user', 'user_name', 'action', 'details', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return data