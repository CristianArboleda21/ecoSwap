from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..services.publications_service import PublicationsService
from ..serializers import PublicationsSerializer, CategorySerializer, StateSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_publication(request):
    user = request.user

    titulo = request.data.get('titulo')
    descripcion = request.data.get('descripcion')
    categoria_id = request.data.get('categoria_id')
    estado_id = request.data.get('estado_id')
    ubicacion = request.data.get('ubicacion')
    imagenes = request.FILES.getlist('imagenes', [])

    if not titulo or not descripcion or not categoria_id or not estado_id:
        return Response(
            {"error": "Todos los campos requeridos: titulo, descripcion, categoria_id, estado_id", "status": 400},
            status=status.HTTP_400_BAD_REQUEST
        )

    success, pub_or_msg = PublicationsService.create_publication(
        user.id, categoria_id, estado_id, titulo, descripcion, ubicacion, imagenes
    )

    if success:
        serializer = PublicationsSerializer(pub_or_msg)
        return Response({"message": "Publicación creada", "publication": serializer.data, "status": 201},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"error": pub_or_msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_publication(request, pub_id):
    user = request.user

    titulo = request.data.get('titulo')
    descripcion = request.data.get('descripcion')
    categoria_id = request.data.get('categoria_id')
    estado_id = request.data.get('estado_id')
    ubicacion = request.data.get('ubicacion')
    nuevas_imagenes = request.FILES.getlist('imagenes', [])

    success, msg = PublicationsService.update_publication(
        pub_id, categoria_id, estado_id, titulo, descripcion, ubicacion, nuevas_imagenes
    )

    if success:
        return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_publications(request):
    estado_id = request.query_params.get('estado_id')
    success, publicaciones = PublicationsService.list_publications(estado_id)
    serializer = PublicationsSerializer(publicaciones, many=True)
    return Response({"publications": serializer.data, "status": 200}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_publication(request, pub_id):
    success, pub_or_msg = PublicationsService.get_publication(pub_id)
    if success:
        serializer = PublicationsSerializer(pub_or_msg)
        return Response({"publication": serializer.data, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": pub_or_msg, "status": 404}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def publications_by_category(request, categoria_id):
    success, publicaciones = PublicationsService.list_publications_by_category(categoria_id)
    serializer = PublicationsSerializer(publicaciones, many=True)
    return Response({"publications": serializer.data, "status": 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_favorite(request, pub_id):
    user = request.user
    success, msg = PublicationsService.add_favorite(user.id, pub_id)
    if success:
        return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_favorite(request, pub_id):
    user = request.user
    success, msg = PublicationsService.remove_favorite(user.id, pub_id)
    if success:
        return Response({"message": msg, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": msg, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_favorites(request):
    user = request.user
    success, publicaciones = PublicationsService.list_favorites(user.id)
    serializer = PublicationsSerializer(publicaciones, many=True)
    return Response({"favorites": serializer.data, "status": 200}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_publications(request):
    user = request.user
    success, publicaciones = PublicationsService.list_user_publications(user.id)
    serializer = PublicationsSerializer(publicaciones, many=True)
    return Response({"publications": serializer.data, "status": 200}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    nombre = request.data.get("nombre")

    if not nombre:
        return Response(
            {"error": "El campo 'nombre' es requerido.", "status": 400},
            status=status.HTTP_400_BAD_REQUEST
        )

    success, message, *data = PublicationsService.create_category(nombre)

    if success:
        categoria_id = data[0] if data else None
        return Response({"message": message, "id": categoria_id, "status": 201},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"error": message, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    success, categorias = PublicationsService.list_categories()
    serializer = CategorySerializer(categorias, many=True)
    return Response({"categories": serializer.data, "status": 200}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category(request, categoria_id):
    success, categoria = PublicationsService.get_category(categoria_id)

    if success:
        serializer = CategorySerializer(categoria)
        return Response({"category": serializer.data, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": categoria, "status": 404}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_state(request):
    nombre = request.data.get("nombre")

    if not nombre:
        return Response(
            {"error": "El campo 'nombre' es requerido.", "status": 400},
            status=status.HTTP_400_BAD_REQUEST
        )

    success, message, *data = PublicationsService.create_state(nombre)

    if success:
        estado_id = data[0] if data else None
        return Response({"message": message, "id": estado_id, "status": 201},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({"error": message, "status": 400}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_states(request):
    success, estados = PublicationsService.list_states()
    serializer = StateSerializer(estados, many=True)
    return Response({"states": serializer.data, "status": 200}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_state(request, estado_id):
    success, estado = PublicationsService.get_state(estado_id)

    if success:
        serializer = StateSerializer(estado)
        return Response({"state": serializer.data, "status": 200}, status=status.HTTP_200_OK)
    else:
        return Response({"error": estado, "status": 404}, status=status.HTTP_404_NOT_FOUND)

