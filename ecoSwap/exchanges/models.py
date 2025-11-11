from django.db import models
from publications.models import Publications

# Create your models here.
class Exchange(models.Model):

    class Status(models.TextChoices):
        PENDING = "Pendiente"
        IN_PROCESS = "En Proceso"
        ACCEPTED = "Aceptada"
        REJECTED = "Rechazada"
        CANCELLED = "Cancelada"
        # COMPLETED = "Completada"

    # Item que recibe la oferta (publicación del dueño)
    requested_item = models.ForeignKey(
        Publications,
        on_delete=models.PROTECT,
        related_name="exchange_requests"
    )

    # Item ofrecido por el usuario que quiere el intercambio
    offered_item = models.ForeignKey(
        Publications,
        on_delete=models.PROTECT,
        related_name="exchange_offers"
    )

    # Estado de la oferta
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


