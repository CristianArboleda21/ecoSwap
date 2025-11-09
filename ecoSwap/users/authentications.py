from rest_framework.authentication import BaseAuthentication 
from rest_framework.exceptions import AuthenticationFailed 
from .services.jwt_service import JWTService 
from .models import Users

class CustomJWTAuthentication(BaseAuthentication): 
    """ Autenticación JWT personalizada """ 
    
    def authenticate(self, request): 
        """ Autentica la petición usando el token JWT del header """ 
        auth_header = request.META.get('HTTP_AUTHORIZATION', '') 
        
        if not auth_header: 
            return None # No hay header, dejar que otro authenticator lo maneje 
        
        # Verificar formato: "Bearer <token>" 
        parts = auth_header.split() 
        if len(parts) != 2: 
            return None 
        
        if parts[0].lower() != 'bearer': 
            return None 
        
        token = parts[1] 
        
        # Verificar el access token 
        payload, error = JWTService.verify_access_token(token) 
        if error: 
            raise AuthenticationFailed(error) 
        
        # Obtener usuario 
        email = payload.get('email') 
        if not email:
             raise AuthenticationFailed('Token no contiene email') 
        
        user = Users.objects.filter(email=email.lower()).first()
        if not user: 
            raise AuthenticationFailed('Usuario no encontrado') 
        
        # Retornar (user, token) 
        return (user, token) 
    
    def authenticate_header(self, request): 
        return 'Bearer realm="api"'