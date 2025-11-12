from django.contrib.auth.models import AbstractUser
from passlib.hash import pbkdf2_sha256
from django.db import models

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10,unique=True)
    password = models.CharField(max_length=256)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires = models.DateTimeField(blank=True, null=True)
    refresh_token_expires = models.DateTimeField(blank=True, null=True)

    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_expires = models.DateTimeField(blank=True, null=True)
    reset_code_used = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def set_password(self, password: str): 
        """Encripta y guarda la contraseña usando PBKDF2-SHA256""" 
        try: 
            if not password: 
                raise ValueError("La contraseña no puede estar vacía")
            
            #Hash de la contraseña 
            self.password = pbkdf2_sha256.hash(password) 

        except Exception as e: 
            raise 
    
    def check_password(self, password: str) -> bool: 
        """Verifica si la contraseña es correcta""" 
        try: 
            if not password or not self.password: 
                return False
            
            # Verificar la contraseña 
            return pbkdf2_sha256.verify(password, self.password) 
        
        except Exception as e: 
            raise

class ImagesUsers(models.Model):
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    image: models.TextField = models.TextField()
    uploaded_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)