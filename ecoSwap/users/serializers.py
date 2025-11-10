from rest_framework import serializers
from .models import User, ImagesUsers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'reputation', 'address', 'created_at']

class ImagesUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesUsers
        fields = '__all__'