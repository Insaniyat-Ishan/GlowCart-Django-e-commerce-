from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import Address
from orders.models import Order
from orders.utils import get_store_metrics

@login_required
def profile(request):
    # your regular profile data
    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-id")
    recent_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]

    ctx = {
        "addresses": addresses,
        "recent_orders": recent_orders,
    }

    # staff-only metrics
    if request.user.is_staff:
        ctx["store_metrics"] = get_store_metrics()

    return render(request, "accounts/profile.html", ctx)

from orders.utils import get_store_metrics
from .models import Address

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        email = request.POST.get("email", "").strip()
        if not username or not password:
            return render(request, "accounts/register.html", {"error": "Username and password are required."})
        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {"error": "Username already taken."})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("profile")
    return render(request, "accounts/register.html")

@login_required
def profile(request):
    # your regular profile data
    addresses = Address.objects.filter(user=request.user).order_by("-is_default", "-id")
    recent_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]

    ctx = {
        "addresses": addresses,
        "recent_orders": recent_orders,
    }

    # staff-only metrics
    if request.user.is_staff:
        ctx["store_metrics"] = get_store_metrics()

    return render(request, "accounts/profile.html", ctx)

@login_required
def address_create(request):
    if request.method == "POST":
        addr = Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name", ""),
            phone=request.POST.get("phone", ""),
            line1=request.POST.get("line1", ""),
            line2=request.POST.get("line2", ""),
            city=request.POST.get("city", ""),
            postcode=request.POST.get("postcode", ""),
            country=request.POST.get("country", "Bangladesh"),
            is_default=bool(request.POST.get("is_default")),
        )
        if addr.is_default:
            Address.objects.filter(user=request.user).exclude(id=addr.id).update(is_default=False)
        return redirect("profile")
    return render(request, "accounts/address_form.html")

@login_required
def address_make_default(request, pk):
    addr = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    addr.is_default = True
    addr.save()
    return redirect("profile")

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    messages.info(request, "You’ve been logged out.")
    return redirect("home")  # uses your core.urls `name="home"`

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from catalog.models import Product
from .models import WishlistItem

@login_required
def wishlist_toggle(request, product_id):
    p = get_object_or_404(Product, id=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=p)
    if created:
        messages.success(request, "Added to your wishlist.")
    else:
        item.delete()
        messages.info(request, "Removed from your wishlist.")
    next_url = request.POST.get("next") or request.GET.get("next") or p.get_absolute_url()
    return redirect(next_url)

@login_required
def wishlist_page(request):
    items = (WishlistItem.objects
             .select_related("product", "product__brand", "product__category")
             .filter(user=request.user))
    return render(request, "accounts/wishlist.html", {"items": items})

