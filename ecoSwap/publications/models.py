from django.db import models
from users.models import UserApp

class Category(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

class State(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

class Publications(models.Model):
    id_publicacion = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(UserApp, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

class FavoritePublication(models.Model):
    user = models.ForeignKey(UserApp, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publications, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

class PublicationImage(models.Model):
    publicacion = models.ForeignKey(
        Publications,
        related_name="imagenes",
        on_delete=models.CASCADE
    )
    imagen = models.ImageField(upload_to='publications/')
    fecha = models.DateTimeField(auto_now_add=True)
