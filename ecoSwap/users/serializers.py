from rest_framework import serializers
from .models import Users, ImagesUsers

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name', 'email', 'phone', 'reputation', 'address', 'created_at']

class ImagesUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesUsers
        fields = '__all__'