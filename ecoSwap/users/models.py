from django.db import models

# Create your models here.
class Users(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    email: models.EmailField = models.EmailField(unique=True)
    phone: models.CharField = models.CharField(max_length=10,unique=True)
    password: models.CharField = models.CharField(max_length=64)
    reputation: models.IntegerField = models.IntegerField(default=0)
    address: models.CharField = models.CharField(max_length=100)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

class ImagesUsers(models.Model):
    user: models.ForeignKey = models.ForeignKey(Users, on_delete=models.CASCADE)
    image: models.TextField = models.TextField()
    uploaded_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)