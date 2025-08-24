# core/context_processors.py
from django.conf import settings

CART_SESSION_KEY = "cart"

def cart(request):
    """Cart item count for navbar."""
    cart = request.session.get(CART_SESSION_KEY, {})
    count = sum(cart.values()) if isinstance(cart, dict) else 0
    return {"cart_count": count}

def auth_presets(request):
    """Optional presets for auth page backgrounds (safe defaults)."""
    return {
        "AUTH_LOGIN_PRESET": getattr(settings, "AUTH_LOGIN_PRESET", "auth-minimal"),
        "AUTH_REGISTER_PRESET": getattr(settings, "AUTH_REGISTER_PRESET", "auth-portrait"),
    }

def wishlist_count(request):
    """Wishlist count for navbar."""
    try:
        if request.user.is_authenticated:
            return {"wishlist_count": request.user.wish_items.count()}
    except Exception:
        pass
    return {"wishlist_count": 0}

def nav_categories(request):
    """Top categories for the Shop dropdown."""
    try:
        from catalog.models import Category
        return {"nav_categories": Category.objects.order_by("name")[:10]}
    except Exception:
        return {"nav_categories": []}

from catalog.models import Category

def nav_categories(request):
    try:
        return {"nav_categories": Category.objects.order_by("name")[:10]}
    except Exception:
        return {"nav_categories": []}

def wishlist(request):
    if request.user.is_authenticated:
        from accounts.models import WishlistItem
        return {"wishlist_count": WishlistItem.objects.filter(user=request.user).count()}
    return {"wishlist_count": 0}
