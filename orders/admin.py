from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "unit_price", "qty")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "subtotal", "discount_total", "total", "coupon_code", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)  # inline change in the table
    inlines = [OrderItemInline]
    actions = ["mark_paid", "mark_cancelled"]

    @admin.action(description="Mark selected orders as Paid")
    def mark_paid(self, request, queryset):
        updated = queryset.update(status="paid")
        self.message_user(request, f"{updated} order(s) marked as Paid.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="cancelled")
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")

from django.contrib import admin
from .models import Order, OrderItem, ShippingMethod

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price", "is_active")
    list_editable = ("price", "is_active")
    search_fields = ("name", "code")
