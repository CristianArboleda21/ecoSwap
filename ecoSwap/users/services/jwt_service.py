from datetime import datetime, timedelta, timezone 
from typing import Optional, Dict, Tuple 
from django.conf import settings 
import jwt, uuid

class JWTService:
    """Servicio para manejo de JWT tokens"""
    
    @staticmethod
    def generate_tokens(user) -> Dict[str, str]:
        """Genera access token y refresh token para un usuario
            Returns: 
            { 
                "access": "eyJ0eXAiOiJKV1...",
                "refresh": "eyJ0eXAiOiJKV1...", 
                "access_expires": "2024-01-20T11:00:00Z",
                "refresh_expires": "2024-01-27T10:00:00Z"
            } 
        """  
        now = datetime.now(timezone.utc)  

        # JTI (JWT ID) único para cada token   
        access_jti = str(uuid.uuid4())   
        refresh_jti = str(uuid.uuid4())  

        # Access Token (1 hora)   
        access_expires = now + timedelta(hours=24)   
        access_payload = {  
            'email': user.email,  
            'token_type': 'access',  
            'exp': access_expires,  
            'iat': now,  
            'jti': access_jti
        }  

        # Refresh Token (7 días)   
        refresh_expires = now + timedelta(days=2)
        refresh_payload = {
            'email': user.email,  
            'token_type': 'refresh',
            'exp': refresh_expires, 
            'iat': now, 
            'jti': refresh_jti 
        } 

        #Generar tokens 
        access_token = jwt.encode( 
            access_payload, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM 
        ) 
        
        refresh_token = jwt.encode( 
        refresh_payload, 
        settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM 
        ) 

        # Guardar refresh token ID en el usuario 
        # user.add_refresh_token(refresh_jti) 
        user.save() 

        return { 
            'access': access_token, 
            'refresh': refresh_token, 
            'access_expires': access_expires.isoformat(), 
            'refresh_expires': refresh_expires.isoformat() 
            }  
    
    @staticmethod  
    def extract_jti(token: str) -> str: 
        """Extrae el JTI (JWT ID) del token sin verificar""" 
        try: 
            decoded = jwt.decode(token, options={"verify_signature": False}) 
            return decoded.get('jti', '') 
        except Exception as e: 
            return ''  
    
    @staticmethod  
    def verify_access_token(token: str) -> Tuple[Optional[Dict], Optional[str]]: 
        """ 
        Verifica un access token 
        Returns: 
        (payload, error_message) 
        """ 
        try: 
            payload = jwt.decode( 
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM] 
            ) 

            #Verificar tipo de token 
            if payload.get('token_type') != 'access': 
                return None, "Token inválido" 
            
            return payload, None 
        
        except jwt.ExpiredSignatureError: 
            return None, "Token expirado" 
        except jwt.InvalidTokenError as e: 
            return None, f"Token inválido: {str(e)}"  
    
    @staticmethod  
    def verify_refresh_token(token: str) -> Tuple[Optional[Dict], Optional[str]]: 
        """ 
        Verifica un refresh token 
        Returns: 
        (payload, error_message) 
        """ 
        try: 
            payload = jwt.decode( 
                token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM] 
            ) 
            # Verificar tipo de token 
            if payload.get('token_type') != 'refresh': 
                return None, "Token inválido" 
            
            return payload, None 
        except jwt.ExpiredSignatureError: 
            return None, "Refresh token expirado" 
        except jwt.InvalidTokenError as e: 
            return None, f"Token inválido: {str(e)}"