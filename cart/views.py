# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from catalog.models import Product
from promotions.models import Coupon
from django.contrib import messages
from catalog.models import Product
from catalog.models import ProductVariant  # ← add


CART_SESSION_KEY = "cart"

def _get_cart(session):
    return session.get(CART_SESSION_KEY, {})

def _save_cart(session, cart):
    session[CART_SESSION_KEY] = cart
    session.modified = True

# ✅ Add key parser helper (place near other helpers)
def _parse_cart_key(key: str):
    """Return (product_id, variant_id or None) from cart key."""
    if "-" in key:
        pid, vid = key.split("-", 1)
        return int(pid), int(vid)
    return int(key), None


# cart/views.py
from django.contrib import messages

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if request.method == "POST":
        try:
            qty = int(request.POST.get("qty", 1))
        except ValueError:
            qty = 1
        qty = max(1, qty)

        variant_id = request.POST.get("variant_id")
        variant = None
        if variant_id:
            variant = get_object_or_404(ProductVariant, pk=int(variant_id), product=product, is_active=True)

        # stock checks
        available = variant.stock if variant else product.stock
        if available <= 0:
            messages.error(request, "Sorry, this item is out of stock.")
            return redirect(product.get_absolute_url())

        cart = _get_cart(request.session)
        key = f"{product_id}-{variant.id}" if variant else str(product_id)
        in_cart = int(cart.get(key, 0))
        can_add = max(0, available - in_cart)
        if can_add <= 0:
            messages.warning(request, "You already have the maximum available quantity in your cart.")
        else:
            add_qty = min(qty, can_add)
            cart[key] = in_cart + add_qty
            _save_cart(request.session, cart)
            label = f"{product.title}" + (f" ({variant.name})" if variant else "")
            messages.success(request, f"Added {add_qty} × “{label}” to cart.")
    return redirect("cart_detail")



def remove_from_cart(request, key):
    cart = _get_cart(request.session)
    if key in cart:
        del cart[key]
        _save_cart(request.session, cart)
        messages.info(request, "Item removed.")
    return redirect("cart_detail")


def cart_detail(request):
    cart = _get_cart(request.session)
    items = []
    subtotal = Decimal("0.00")

    for key, qty in cart.items():
        pid, vid = _parse_cart_key(key)
        product = get_object_or_404(Product, id=pid)
        variant = None
        unit_price = product.price
        if vid:
            variant = get_object_or_404(ProductVariant, id=vid, product=product)
            unit_price = variant.display_price
        line_total = (unit_price or Decimal("0.00")) * int(qty)
        items.append({"key": key, "product": product, "variant": variant, "qty": qty, "line_total": line_total})
        subtotal += line_total

    coupon_code = request.session.get("coupon_code")
    coupon = Coupon.objects.filter(code=coupon_code).first() if coupon_code else None
    discount = coupon.discount_for(subtotal) if coupon else Decimal("0.00")
    total = (subtotal - discount).quantize(Decimal("0.01"))

    return render(request, "cart/detail.html", {
        "items": items,
        "subtotal": subtotal,
        "coupon": coupon,
        "discount": discount,
        "total": total,
    })



def apply_coupon(request):
    if request.method == "POST":
        code = (request.POST.get("code") or "").strip().upper()
        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            messages.error(request, "Invalid coupon.")
            request.session.pop("coupon_code", None)
        else:
            request.session["coupon_code"] = coupon.code
            messages.success(request, "Coupon applied.")
        request.session.modified = True
    return redirect("cart_detail")

def remove_coupon(request):
    request.session.pop("coupon_code", None)
    request.session.modified = True
    messages.info(request, "Coupon removed.")
    return redirect("cart_detail")
