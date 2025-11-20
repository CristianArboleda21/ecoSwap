from rest_framework import serializers
from .models import Publications, FavoritePublication, Category, State, PublicationImage, Condition


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'nombre']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'nombre']

class FavoritePublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoritePublication
        fields = ['user', 'publicacion', 'fecha']
        read_only_fields = ['fecha']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'nombre']

class PublicationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationImage
        fields = ['id', 'imagen', 'fecha']
        read_only_fields = ['fecha']

class PublicationsSerializer(serializers.ModelSerializer):
    imagenes = PublicationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Publications
        fields = [
            'id_publicacion',
            'user',
            'categoria',
            'estado',
            'condition',
            'titulo',
            'descripcion',
            'ubicacion',
            'fecha_publicacion',
            'imagenes',
        ]
        read_only_fields = ['id_publicacion', 'fecha_publicacion']