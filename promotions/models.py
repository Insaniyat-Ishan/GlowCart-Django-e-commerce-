from django.db import models
from decimal import Decimal
from django.utils import timezone

class Coupon(models.Model):
    TYPE_CHOICES = [("percent", "Percent"), ("fixed", "Fixed amount")]
    code = models.CharField(max_length=30, unique=True)
    ctype = models.CharField(max_length=10, choices=TYPE_CHOICES, default="percent")
    value = models.DecimalField(max_digits=8, decimal_places=2)  # 10 for 10% or 10.00 fixed
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_live(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True

    def discount_for(self, subtotal: Decimal) -> Decimal:
        if not self.is_live() or subtotal < self.min_amount:
            return Decimal("0.00")
        if self.ctype == "percent":
            return (subtotal * (self.value / Decimal("100"))).quantize(Decimal("0.01"))
        return min(self.value, subtotal).quantize(Decimal("0.01"))
