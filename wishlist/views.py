from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Product
from .models import WishItem

@login_required
def wishlist_page(request):
    items = (WishItem.objects.filter(user=request.user)
             .select_related("product", "product__brand", "product__category"))
    return render(request, "wishlist/page.html", {"items": items})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wi, created = WishItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        wi.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        messages.success(request, "Added to wishlist.")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/wishlist/"
    return redirect(next_url)
