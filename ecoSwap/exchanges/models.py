from django.db import models
from publications.models import Publications

class Exchange(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pendiente"
        IN_PROCESS = "En Proceso"
        ACCEPTED = "Aceptada"
        REJECTED = "Rechazada"
        CANCELLED = "Cancelada"

    requested_item = models.ForeignKey(
        Publications, 
        on_delete=models.PROTECT,
        related_name="exchange_requests"
    )
    offered_item = models.ForeignKey(
        Publications, 
        on_delete=models.PROTECT,
        related_name="exchange_offers"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)