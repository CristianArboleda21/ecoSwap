from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User

from ..services.reputation_service import ReputationService

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_exchange(request):
    exchange_id = request.data.get("exchange_id")
    rating = request.data.get("rating")
    comment = request.data.get("comment", "")

    user = request.user

    success, message = ReputationService.rate_exchange(user, exchange_id, rating, comment)

    if not success:
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": message}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reputation(request):

    user = request.user
    user_id = user.id

    try:
        reputation = ReputationService.get_reputation(user_id)
    except Exception as e:
        return Response({"error": "No se pudo obtener la reputación."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(reputation, status=status.HTTP_200_OK)

    