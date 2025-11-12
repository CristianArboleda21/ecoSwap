from typing import Optional, Dict, Tuple 
from datetime import datetime, timedelta
from comunications.services.email_service import EmailService 
from passlib.hash import pbkdf2_sha256
from .jwt_service import JWTService 
from ..models import User
from django.utils import timezone

import re, random

class AuthService: 
    """Servicio de autenticación con JWT"""
    
    MIN_PASSWORD_LENGTH = 8
    
    @classmethod
    def validate_email(cls, email: str) -> bool:  
        """Valida formato de email"""  
        pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  
        return re.match(pattern, email) is not None
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:  
        """Valida requisitos de contraseña"""  
        if len(password) < cls.MIN_PASSWORD_LENGTH:  
            return False, f"La contraseña debe tener al menos {cls.MIN_PASSWORD_LENGTH} caracteres"  
        if not re.search(r'[A-Z]', password):  
            return False, "La contraseña debe contener al menos una mayúscula"  
        if not re.search(r'[a-z]', password):  
            return False, "La contraseña debe contener al menos una minúscula"  
        if not re.search(r'\d', password):  
            return False, "La contraseña debe contener al menos un número"  
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  
            return False, "La contraseña debe contener al menos un carácter especial"  
        
        return True, "OK"
    
    @classmethod
    def create_user(cls, name: str, email: str, phone: str, password: str, address: str) -> User:  
        """Crea un nuevo usuario"""  

        # Validar email  
        if not cls.validate_email(email):  
            return None, "Email inválido"  
        
        # Validar contraseña  
        valid, msg = cls.validate_password(password)  
        if not valid:  
            return None, msg  
        
        # Verificar si ya existe  
        user_exist = User.objects.filter(email=email).first()
        if user_exist:  
            return None, "El email ya está registrado" 
         
        try:  
            # Crear usuario  
            username=f"{name.split(' ')[0]}{random.randint(1000,9999)}"
            user = User.objects.create(name=name, email=email.lower(), phone=phone, address=address, username=username)  
            user.set_password(password)  
            user.save()  
              
            return user, "Usuario creado exitosamente"  
        
        except Exception as e:  
            return None, f"Error al crear usuario: {str(e)}"
        
    @classmethod
    def login(cls, email: str, password: str) -> Tuple[Optional[Dict], str]:  
        """  
        Autentica usuario y genera tokens JWT  
        """  
        try:  
            # Buscar usuario  
            user = User.objects.filter(email=email.lower()).first()  

            if not user:  
                return None, "Usuario no encontrado"    
            
            # Verificar contraseña  
            if not user.check_password(password):   
                return None, f"Contraseña incorrecta."  
       
            # Generar JWT token  
            tokens = JWTService.generate_tokens(user)  

            # Actualizar último login y resetear intentos 
            user.token = tokens['access']  
            user.refresh_token = tokens['refresh']
            user.token_expires = tokens['access_expires']  
            user.refresh_token_expires = tokens['refresh_expires']
            user.save()

            return {  
                "access": tokens['access'],  
                "refresh": tokens['refresh'],  
                "access_expires": tokens['access_expires'],  
                "refresh_expires": tokens['refresh_expires'],  
                "name": user.name,  
                "email": user.email,  
                "status" : 200  
            }, "Login exitoso"  
        
        except Exception as e:  
            return None, f"Error al iniciar sesión: {str(e)}"
        
    @classmethod
    def verify_token(cls, token: str) -> Tuple[Optional[User], str]:  
        """Verifica un access token y retorna el usuario"""  

        payload, msg = JWTService.verify_access_token(token)  
        if not payload:  
            return None, "Usuario no logueado"
        
        # Obtener usuario  
        email = payload.get('email')  
        user = User.objects.filter(email=email).first()  
        if not user:  
            return None, msg
        
        return user, msg
    
    @classmethod
    def request_password_reset(cls, email: str):

        user = User.objects.filter(email=email.lower()).first()  
        if not user:  
            return False, "Usuario no encontrado"
        
        # Generar código de reseteo
        reset_code = str(random.randint(100000, 999999))
        user.reset_code = reset_code
        user.reset_code_expires = timezone.now() + timedelta(minutes=15)
        user.reset_code_used = False
        user.save()

        email_sent = EmailService.send_email(
            to_email=email,
            reason='reset_code',
            user_name=user.name,
            reset_code=reset_code,
        )

        if not email_sent:
            return False, "Error al enviar email de restablecimiento"
        
        return True, "Código de restablecimiento enviado exitosamente"
    
    @classmethod
    def reset_password_with_token(cls, email: str, code: str, new_password: str, confirm_password: str):
        """Restablece la contraseña usando el código de reseteo enviado por email"""
        
        user = User.objects.filter(email=email.lower()).first()  
        if not user:  
            return False, "Usuario no encontrado"
        
        # Verificar código
        if user.reset_code != code:
            return False, "Código de restablecimiento inválido"
        
        if user.reset_code_used:
            return False, "El código de restablecimiento ya fue usado"
        
        if timezone.now() > user.reset_code_expires:
            print(timezone.now())
            return False, "El código de restablecimiento ha expirado"
        
        if new_password != confirm_password:
            return False, "Las contraseñas no coinciden"
        
        # Validar nueva contraseña
        valid, msg = cls.validate_password(new_password)  
        if not valid:  
            return False, msg  
        
        # Actualizar contraseña
        user.set_password(new_password)
        user.reset_code_used = True
        user.save()
        
        return True, "Contraseña restablecida exitosamente"
    
    @classmethod
    def logout(cls, user: User) -> bool:
        """Cierra la sesión del usuario invalidando sus tokens"""
        try:
            user.token = None
            user.refresh_token = None
            user.token_expires = None
            user.refresh_token_expires = None
            user.save()
            return True, "Sesión cerrada correctamente"
        except Exception as e:
            return False, f"Error al cerrar sesión: {str(e)}"
    
    # @classmethod
    # def refresh_token(cls, refresh_token: str) -> Tuple[Optional[Dict], str]:  
    #     """  
    #      Refresca el access token usando refresh token  
    #      Args:  
    #     refresh_token: El refresh token del usuario  
    #      Returns:  
    #     Tuple (tokens_dict, error_message)  
    #     - tokens_dict: Dict con los nuevos tokens (None si falla)  
    #     - error_message: Mensaje de error (None si es exitoso)  
    #      """  
        
    #     try:  
    #         # Verificar refresh token  
    #         payload, error = JWTService.verify_refresh_token(refresh_token)  
    #         if error:  
                  
    #             return None, error  
            
    #         # Obtener usuario  
    #         email = payload.get('email')  
    #         user = User.objects(email=email).first()  
            
    #         if not user:  
    #             return None, "Usuario no encontrado"  
    #         if not user.is_active:  
    #             return None, "Usuario inactivo"  
            
    #         # Verificar que el refresh token guardado coincida  
    #         if user.app_refresh_token != refresh_token:  
    #             return None, "Refresh token no coincide con el registrado"  
            
    #         # Verificar que no esté en blacklist  
    #         refresh_jti = JWTService.extract_jti(refresh_token)  
    #         if user.is_token_blacklisted(refresh_jti):  
    #             return None, "Refresh token revocado"  
        
    #         # Generar nuevos tokens  
    #         tokens = JWTService.generate_tokens(user)  
    #         new_refresh_jti = JWTService.extract_jti(tokens['refresh'])  
    #         old_refresh_jti = JWTService.extract_jti(refresh_token)  
    #         # Actualizar tokens en BD  
    #         user.update(  
    #             setapp_token=tokens['access'],  
    #             setapp_refresh_token=tokens['refresh'],  
    #             setapp_token_expires=tokens['access_expires'],  
    #             setapp_refresh_token_expires=tokens['refresh_expires']  
    #         )  
    #         user.update(  
    #             pullrefresh_tokens=old_refresh_jti  
    #         )  
    #         user.update(  
    #             push_refresh_tokens=new_refresh_jti  
    #         )  
    #         return tokens, None 
         
    #     except Exception as e:  
              
    #         return None, "Error al refrescar token"