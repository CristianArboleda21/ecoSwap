from rest_framework import serializers
from .models import UserApp, ImagesUsers

class UserAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApp
        fields = ['name', 'email', 'phone', 'address', 'created_at']

class ImagesUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesUsers
        fields = ['image', 'uploaded_at']