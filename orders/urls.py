from django.urls import path
from .views import admin_metrics, checkout, order_detail, my_orders
from .views import invoice_view


urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("orders/<int:pk>/", order_detail, name="order_detail"),
    path("my-orders/", my_orders, name="my_orders"),  # ← new
    path("orders/<int:pk>/invoice/", invoice_view, name="order_invoice"),
    path("dashboard/metrics/", admin_metrics, name="admin_metrics"),
]

