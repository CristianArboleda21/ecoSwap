from django.db import models
from users.models import UserApp
from exchanges.models import Exchange

class Reputation(models.Model):
    user = models.OneToOneField(
        UserApp, 
        on_delete=models.CASCADE,
        related_name="reputation_profile"   # ✅ evita choque con User.reputation
    )
    score = models.FloatField(default=0)

    def update_score(self):
        ratings = detailReputation.objects.filter(rated_user=self.user)
        if ratings.exists():
            self.score = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.save()


class detailReputation(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)

    rated_user = models.ForeignKey(
        UserApp, 
        on_delete=models.CASCADE,
        related_name='received_reviews'    # nombre único
    )

    reviewer = models.ForeignKey(
        UserApp, 
        on_delete=models.CASCADE,
        related_name='written_reviews'     # nombre único
    )

    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exchange', 'reviewer')
