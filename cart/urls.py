# cart/urls.py
from django.urls import path
from django.urls import path
from .views import cart_detail, add_to_cart, remove_from_cart, apply_coupon, remove_coupon

urlpatterns = [
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<slug:key>/", remove_from_cart, name="remove_from_cart"),  # ← was <int:product_id>
    path("cart/apply-coupon/", apply_coupon, name="apply_coupon"),
    path("cart/remove-coupon/", remove_coupon, name="remove_coupon"),
]
