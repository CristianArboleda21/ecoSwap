from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..services.exchange_service import ExchangeService
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exchange(request):
    """ Crea una nueva oferta de intercambio """

    request_item = request.data.get("request_item")
    offered_item = request.data.get("offered_item")
    status_exchange = request.data.get("status")

    success, message = ExchangeService.create_exchange(request_item, offered_item, status_exchange)

    if not success:
        return Response(
            {"error": "No se envio el intercambio", "status": 400},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({"message": message}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_exchange(request):
    """ Responde a una oferta de intercambio """

    # Lógica para responder a una oferta de intercambio
    exchange = request.data.get("exchange_id")
    response_status = request.data.get("status")

    success, message = ExchangeService.respond_exchange(exchange, response_status)

    if not success:
        return Response(
            {"error": "No se pudo responder a la oferta de intercambio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"message": message}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_exchange(request):
    """ Cancela una oferta de intercambio """

    exchange_id = request.data.get("exchange_id")
    reason = request.data.get("reason")
    user = request.user

    success, message = ExchangeService.cancel_exchange(exchange_id, user.email, reason)

    if not success:
        return Response(
            {"error": message},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"message": message}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exchanges(request):
    """ Lista todas las ofertas de intercambio """

    st = request.query_params.get("status", None)
    exchange_type = request.query_params.get("type", None)
    user = request.user

    exchanges = ExchangeService.list_exchanges(user.email, st, exchange_type)

    return Response(exchanges, status=status.HTTP_200_OK)