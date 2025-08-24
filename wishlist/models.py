from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product

class WishItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wish_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.product}"
