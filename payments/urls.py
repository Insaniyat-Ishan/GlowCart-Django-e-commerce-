from django.urls import path
from .views import create_checkout_session, payment_success

urlpatterns = [
    path("payments/create/<int:order_id>/", create_checkout_session, name="create_checkout_session"),
    path("payments/success/", payment_success, name="payment_success"),
]
