from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "ctype", "value", "min_amount", "active", "starts_at", "ends_at")
    list_filter = ("active", "ctype")
    search_fields = ("code",)
