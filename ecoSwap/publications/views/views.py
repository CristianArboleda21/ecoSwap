from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..services.publications_service import PublicationsService
from ..serializers import PublicationsSerializer

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
