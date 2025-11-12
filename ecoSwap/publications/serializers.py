from rest_framework import serializers
from .models import Publications

class PublicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publications
        fields = ['title', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']