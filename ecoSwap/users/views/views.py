from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import AllowAny, IsAuthenticated 
from rest_framework.response import Response 
from ..services.auth_service import AuthService
from ..serializers import UserAppSerializer, ImagesUsersSerializer
from rest_framework import status 
from ..models import UserApp, ImagesUsers
from publications.models import Publications, Category, State
from publications.serializers import PublicationsSerializer

from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os

@api_view(['POST']) 
@permission_classes([AllowAny]) 
def register(request):
    """     Registra un nuevo usuario  """  

    name = request.data.get('name')  
    email = request.data.get('email', '').strip()  
    password = request.data.get('password', '')  
    address = request.data.get('address', '')
    phone = request.data.get('phone', '')
    
    if not email or not password:  
         return Response({"error": "Usuario, email y contraseña son requeridos", "status" : 400},
                         status=status.HTTP_400_BAD_REQUEST)
      
    # Crear usuario  
    user, message = AuthService.create_user(name, email, phone, password, address)  
 
    if user:  
        return Response(
            { 
                "message": message, 
                "user": {
                    "username" : user.name,  
                    "email": user.email,  
                    "created_at": user.created_at.isoformat()  
                },
                "status" : 201  
            }, 
            status=status.HTTP_201_CREATED
        )

    else:  
        return Response({"error": message, "status" : 400}, status=status.HTTP_400_BAD_REQUEST) 
    

@api_view(['POST']) 
@permission_classes([AllowAny]) 
def login(request):  
    """  
    Login con JWT  
    """  
    email = request.data.get('email', '').strip()  
    password = request.data.get('password', '')  

    if not email or not password:  
        return Response({"error": "Email y contraseña son requeridos", "status" : 400}, status=status.HTTP_400_BAD_REQUEST)  
    
    # Autenticar y generar JWT  
    result, message = AuthService.login(email, password)  
    if result:  
        return Response(result, status=status.HTTP_200_OK)  
    else:  
        return Response({"error": message, "status" : 401}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """  
    Obtiene el perfil del usuario autenticado  
    """  
    user: UserApp = request.user  
    
    try:
        image = ImagesUsers.objects.filter(user=user)
        serializer_image = ImagesUsersSerializer(image, many=True)
        serializer = UserAppSerializer(user)
        data = {
            'user': serializer.data,
            'image': serializer_image.data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": f"Error al obtener perfil: {str(e)}", "status": 500}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 
def verify_token(request):  
    """  
    Verifica si un access token es válido  
    """  
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:  
        return Response({"error": "Authorization header con Bearer token es requerido", "status" : 400}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    user = AuthService.verify_token(token)  
    if user:  
        return Response(
            {
                "token_valid": True,  
                "token": token,  
                "email": user.email,  
                "status" : 200  
            }, status=status.HTTP_200_OK)  
    
    else:  
        return Response(
            {  
                "token_valid": False,  
                "token": token,  
                "email": user.email,  
                "status" : 401  
            }, status=status.HTTP_401_UNAUTHORIZED) 
     
@api_view(['POST']) 
@permission_classes([AllowAny]) 
def send_code_password_reset(request):  
    """  
    Paso 1: Solicitar código de restablecimiento  
    Body:  
    {  
        "email": "usuario@example.com"  
    }  
    """  

    email = request.data.get('email')
    if not email:  
        return Response({"error": "Email requerido", "status": 400}, status=status.HTTP_400_BAD_REQUEST)  
     
    result, msg = AuthService.request_password_reset(email)  
    
    return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK) 
     
@api_view(['POST']) 
@permission_classes([AllowAny]) 
def reset_password_code(request):  
    """  
    Paso 2: Restablecer contraseña con código  
    Body:  
    {  
        "email": "usuario@example.com",  
        "code": "123456",  
        "new_password": "NuevaContraseña123",  
        "confirm_password": "NuevaContraseña123"  
    }  
    """  

    email = request.data.get('email')  
    code = request.data.get('code')  
    new_password = request.data.get('new_password')  
    confirm_password = request.data.get('confirm_password')  
    
    if not all([email, code, new_password, confirm_password]):  
        return Response({"error": "Todos los campos son requeridos", "status": 400}, status=status.HTTP_400_BAD_REQUEST)  
    
    result, msg = AuthService.reset_password_with_token(email, code, new_password, confirm_password)  
    
    if result == False:  
        return Response({"error": msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)  
    
    return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK)  


@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def logout(request):  
    """  
    Logout - invalida los tokens del usuario
    """  

    user = request.user 

    if not user:  
        return Response({"error": "El usuario no esta logueado", "status" : 400}, status=status.HTTP_400_BAD_REQUEST)  
     
    # Realizar logout  
    success, msg = AuthService.logout(user) 

    if success:  
        return Response({"message": msg, "status" : 200}, status=status.HTTP_200_OK)
      
    else:  
        return Response({"error": msg, "status" : 400},  status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_by_email(request):

    try:
        user_id = request.query_params.get('email', '')
        
        # Intentar obtener usuario por ID
        try:
            user = UserApp.objects.get(id=int(user_id))
        except (ValueError, UserApp.DoesNotExist):
            # Si falla, intentar por email (para mantener compatibilidad)
            user = UserApp.objects.get(email=user_id)
        
        publications = Publications.objects.filter(user=user.id)
        image = ImagesUsers.objects.filter(user=user)

        # Serializar las publicaciones con toda su estructura
        serializer_publications = PublicationsSerializer(publications, many=True)
        serializer_user = UserAppSerializer(user)
        serializer_image = ImagesUsersSerializer(image, many=True)

        data = {
            'user': serializer_user.data,
            'image': serializer_image.data,
            'publications': serializer_publications.data
        }
        return Response(data, status=status.HTTP_200_OK)

    except UserApp.DoesNotExist:
        return Response(
            {"error": "No existe un usuario con ese ID o email.", "status": 404},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return Response(
            {"error": f"Error al obtener perfil: {str(e)}", "status": 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request):
    """
    Obtiene la información de un usuario por su ID
    """
    try:
        user_id = request.query_params.get('id', '')
        
        if not user_id:
            return Response(
                {"error": "El parámetro 'id' es requerido", "status": 400},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = UserApp.objects.get(id=int(user_id))
        image = ImagesUsers.objects.filter(user=user)
        
        serializer_user = UserAppSerializer(user)
        serializer_image = ImagesUsersSerializer(image, many=True)
        
        data = {
            'user': serializer_user.data,
            'image': serializer_image.data
        }
        return Response(data, status=status.HTTP_200_OK)
    
    except ValueError:
        return Response(
            {"error": "El ID debe ser un número válido", "status": 400},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except UserApp.DoesNotExist:
        return Response(
            {"error": "No existe un usuario con ese ID", "status": 404},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        return Response(
            {"error": f"Error al obtener usuario: {str(e)}", "status": 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_user_profile(request):
    """
    Edita el perfil del usuario autenticado.
    Campos permitidos: name, username, phone, address, image
    """
    try:
        user = request.user
        
        name = request.data.get('name', None)
        username = request.data.get('username', None)
        phone = request.data.get('phone', None)
        address = request.data.get('address', None)
        
        # La imagen puede venir como archivo (FILES) o como string base64 (data)
        image = request.FILES.get('image', None)
        if not image:
            image = request.data.get('image', None)

        success, msg = AuthService.update_user_profile(
            name, username, phone, address, image, user
        )

        if success:
            return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)

    
    except Exception as e:
        return Response(
            {"error": f"Error al actualizar perfil: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )