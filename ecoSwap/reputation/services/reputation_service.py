from reputation.models import Reputation, detailReputation
from exchanges.models import Exchange

class ReputationService:
      
    @classmethod
    def rate_exchange(cls, user, exchange_id, rating, comment):
        try:
            exchange = Exchange.objects.get(id=exchange_id)
        except Exchange.DoesNotExist:
            return False, "El intercambio no existe."

        # Validar usuarios
        if user != exchange.requested_item.user and user != exchange.offered_item.user:
            return False, "No participaste en este intercambio."
        
        # Usuario que será calificado
        rated_user = (
            exchange.offered_item.user 
            if user == exchange.requested_item.user 
            else exchange.requested_item.user
        )

        # Evita doble calificación
        if detailReputation.objects.filter(exchange=exchange, reviewer=user).exists():
            return False, "Ya calificaste este intercambio."

        # Crear calificación
        detailReputation.objects.create(
            exchange=exchange,
            rated_user=rated_user,
            reviewer=user,
            rating=rating,
            comment=comment
        )

        # Actualizar score global
        rep, _ = Reputation.objects.get_or_create(user=rated_user)
        rep.update_score()

        return True, "Calificación registrada con éxito."
    
    @classmethod
    def get_reputation(cls, user_id):
        try:
            details_rate = []
            
            reputation = Reputation.objects.get(user__id=user_id)
            details = detailReputation.objects.filter(rated_user__id=user_id)

            for detail in details:
                details_rate.append({
                    "exchange_id": detail.exchange.id,
                    "reviewer_id": detail.reviewer.id,
                    "rating": detail.rating,
                    "comment": detail.comment,
                    "created_at": detail.created_at
                })

            
            return {
                "score" : reputation.score,
                "details": details_rate
            }
        
        except Reputation.DoesNotExist:
            return None

