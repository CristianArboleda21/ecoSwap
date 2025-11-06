from rest_framework import serializers
from .models import Users, ImagesUsers

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class ImagesUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesUsers
        fields = '__all__'