from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, profile, address_create, address_make_default
from .views import register, profile, address_create, address_make_default, logout_view
from django.urls import path
from .views import wishlist_toggle, wishlist_page
urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),
    path("profile/", profile, name="profile"),
    path("address/new/", address_create, name="address_create"),
    path("address/<int:pk>/default/", address_make_default, name="address_make_default"),
    path("wishlist/", wishlist_page, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", wishlist_toggle, name="toggle_wishlist"),
]
