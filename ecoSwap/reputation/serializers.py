from rest_framework import serializers
from .models import Reputation, detailReputation

class ReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reputation
        fields = '__all__'

class DetailReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = detailReputation
        fields = '__all__'