from comunications.services.email_service import EmailService
from ..serializers import ExchangeSerializer
from publications.models import Publications
from django.utils import timezone
from ..models import Exchange

class ExchangeService:

    @classmethod
    def create_exchange(cls, request_item, offered_item, status_exchange):

        try:
            publication_request = Publications.objects.get(id=request_item)
            publication_offered = Publications.objects.get(id=offered_item)
        except Publications.DoesNotExist:
            return False, "Una de las publicaciones no existe."
        
        exchange = Exchange.objects.create(
            requested_item=publication_request,
            offered_item=publication_offered,
            status=status_exchange,
            created_at=timezone.now(),
            updated_at=None
        )

        publication_request = Publications.objects.get(id=request_item)
        publication_name = publication_request.titulo
        publication_image = publication_request.descripcion

        user = publication_request.user
        email_user = user.email
        user_name = user.name

        email_send = EmailService.send_email(email_user, 'send_exchange', user_name, publication_name, publication_image)

        return True, "Oferta de intercambio enviada."
    
    @classmethod
    def respond_exchange(cls, exchange_id, response_status):

        try:
            exchange = Exchange.objects.get(id=exchange_id)
            publication_request = Publications.objects.get(id=exchange.requested_item.id)
            publication_offered = Publications.objects.get(id=exchange.offered_item.id)

            user_request = publication_request.user
            title_request = publication_request.titulo
            image_request = publication_request.descripcion

            user_offered = publication_offered.user
            title_offered = publication_offered.titulo
            image_offered = publication_offered.descripcion

        except Exchange.DoesNotExist:
            return False, "La oferta de intercambio no existe."
        
        send_email = EmailService.send_email(
            user_offered.email,
            'exchange_response',
            user_offered.name,
            responder_name=user_request.name,
            status_label=response_status,
            request_title=title_request,
            request_image=image_request,
            offered_title=title_offered,
            offered_image=image_offered
        )

        exchange.status = response_status
        exchange.updated_at = timezone.now()
        exchange.save()

        # Aquí podrías agregar lógica adicional, como notificar a los usuarios involucrados

        return True, "Respuesta a la oferta de intercambio fue enviada."
    
    @classmethod
    def cancel_exchange(cls, exchange_id, email_user, reason):

        try:
            exchange = Exchange.objects.get(id=exchange_id)
            publication_request = Publications.objects.get(id=exchange.requested_item.id)
            publication_offered = Publications.objects.get(id=exchange.offered_item.id)
            user_request = publication_request.user
            user_offered = publication_offered.user
        except Exchange.DoesNotExist:
            return False, "La oferta de intercambio no existe."
        
        if exchange.status != Exchange.Status.ACCEPTED:
            return False, "Solo se pueden cancelar ofertas de intercambio que estén en estado 'Aceptada'."
        
        if user_request.email != email_user and user_offered.email != email_user:
            return False, "No tienes permiso para cancelar esta oferta de intercambio, solo quien acepto el intercambio o quien los ofrecio pueden realizar esta acción."
        
        now = timezone.now()

        # Límite de 5 días desde la última actualización (o aceptación)
        limit_date = exchange.updated_at + timezone.timedelta(days=5)

        # Si YA PASÓ el límite → no puede cancelar
        if now > limit_date:
            return False, "No puedes cancelar esta oferta porque ya pasaron más de 5 días."
        
        if user_request.email == email_user:
            email = user_offered.email
        elif user_offered.email == email_user:
            email = user_request.email
        
        exchange.status = Exchange.Status.CANCELLED
        exchange.updated_at = timezone.now()
        exchange.save()

        send_email = EmailService.send_email(
            email,
            'cancel_exchange',
            user_request.name,
            responder_name=user_offered.name,
            status_label=exchange.status,
            request_title=publication_request.titulo,
            request_image=publication_request.descripcion,
            offered_title=publication_offered.titulo,
            offered_image=publication_offered.descripcion,
            extra_message=reason
        )
        
        return True, "Oferta de intercambio cancelada."
    
    @classmethod
    def list_exchanges(cls, email_user, status_filter, exchanges_type):

        try:
            if status_filter == "accepted":
                if exchanges_type == "offered":
                    exchanges = Exchange.objects.filter(
                        offered_item__user__email=email_user,
                        status=Exchange.Status.ACCEPTED
                    )
                else:  # requested
                    exchanges = Exchange.objects.filter(
                        requested_item__user__email=email_user,
                        status=Exchange.Status.ACCEPTED
                    )
            elif status_filter == "cancelled":
                if exchanges_type == "offered":
                    exchanges = Exchange.objects.filter(
                        offered_item__user__email=email_user,
                        status=Exchange.Status.CANCELLED
                    )
                else:  # requested
                    exchanges = Exchange.objects.filter(
                        requested_item__user__email=email_user,
                        status=Exchange.Status.CANCELLED
                    )
            elif status_filter == "pending" or status_filter == "in_progress":
                if exchanges_type == "offered":
                    exchanges = Exchange.objects.filter(
                        offered_item__user__email=email_user,
                        status=Exchange.Status.PENDING
                    )
                else:  # requested
                    exchanges = Exchange.objects.filter(
                        requested_item__user__email=email_user,
                        status=Exchange.Status.PENDING
                    )
            else:
                # Si no hay filtro de status, devolver todos
                if exchanges_type == "offered":
                    exchanges = Exchange.objects.filter(
                        offered_item__user__email=email_user
                    )
                else:  # requested o received
                    exchanges = Exchange.objects.filter(
                        requested_item__user__email=email_user
                    )
        except Exception as e:
            return []
        
        serializer = ExchangeSerializer(exchanges, many=True)
        return serializer.data




