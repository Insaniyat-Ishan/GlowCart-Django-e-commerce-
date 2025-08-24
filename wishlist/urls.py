from django.urls import path
from .views import wishlist_page, toggle_wishlist

urlpatterns = [
    path("wishlist/", wishlist_page, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),
]
