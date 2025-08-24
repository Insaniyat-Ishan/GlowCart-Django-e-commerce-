from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from accounts import models
from catalog.models import Product
from accounts.models import Address
from .models import Order, OrderItem
from promotions.models import Coupon
from catalog.models import ProductVariant
from .models import Order, OrderItem, ShippingMethod

from .models import Order, OrderItem
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Sum, F, ExpressionWrapper, DecimalField


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Product, ProductVariant
from .models import Order, OrderItem, ShippingMethod

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Address
from catalog.models import Product, ProductVariant
from .models import Order, OrderItem, ShippingMethod
CART_SESSION_KEY = "cart"
@login_required
def checkout(request):
    # --- build cart items (variant-aware) ---
    cart = request.session.get("cart", {})
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_detail")

    items, subtotal = [], Decimal("0.00")
    for key, qty in cart.items():
        pid, vid = (int(key.split("-")[0]), int(key.split("-")[1])) if "-" in key else (int(key), None)
        product = get_object_or_404(Product, id=pid, is_active=True)
        variant = ProductVariant.objects.get(id=vid, product=product) if vid else None
        unit_price = variant.display_price if variant else product.price
        line_total = (unit_price or Decimal("0.00")) * int(qty)
        items.append({"product": product, "variant": variant, "qty": int(qty), "unit_price": unit_price, "line_total": line_total})
        subtotal += line_total

    # --- choose shipping (prefer POST, else GET, else cheapest) ---
    code = (request.POST.get("shipping") or request.GET.get("shipping") or "").strip()
    shipping = ShippingMethod.objects.filter(code=code, is_active=True).first() if code else None
    if not shipping:
        shipping = ShippingMethod.objects.filter(is_active=True).order_by("price").first()
    shipping_cost = shipping.price if shipping else Decimal("0.00")

    # --- choose address (prefer POST, else GET, else default, else first) ---
    addresses = Address.objects.filter(user=request.user)
    addr_id = (request.POST.get("address_id") or request.GET.get("address_id") or "").strip()
    selected_address = addresses.filter(id=addr_id).first() if addr_id else None
    if not selected_address:
        selected_address = addresses.filter(is_default=True).first() or addresses.first()
    if not selected_address:
        messages.error(request, "Please add a shipping address first.")
        return redirect("address_create")

    # --- coupons (keep or remove based on your project) ---
    coupon_code = request.session.get("coupon_code")
    discount = Decimal("0.00")
    coupon = None
    try:
        from cart.models import Coupon
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon:
                discount = coupon.discount_for(subtotal)
    except Exception:
        pass

    total = (subtotal - discount + shipping_cost).quantize(Decimal("0.01"))

    if request.method == "POST":
        # create order
        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            status="pending",
            subtotal=subtotal,
            discount_total=discount,
            shipping_method=shipping,
            shipping_cost=shipping_cost,
            total=total,
            coupon_code=coupon.code if coupon else "",
        )

        for it in items:
            OrderItem.objects.create(
                order=order,
                product=it["product"],
                variant=it["variant"],
                unit_price=it["unit_price"],
                qty=it["qty"],
            )
            # reduce stock on the right thing
            if it["variant"]:
                it["variant"].stock = max(0, it["variant"].stock - it["qty"])
                it["variant"].save(update_fields=["stock"])
            else:
                it["product"].stock = max(0, it["product"].stock - it["qty"])
                it["product"].save(update_fields=["stock"])

        # clear cart
        request.session["cart"] = {}
        request.session.modified = True

        messages.success(request, "Order placed.")
        return redirect("order_detail", pk=order.id)

    # GET render
    return render(request, "orders/checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "coupon": coupon,
        "shipping": shipping,
        "shipping_methods": ShippingMethod.objects.filter(is_active=True).order_by("price"),
        "shipping_cost": shipping_cost,
        "total": total,
        "addresses": addresses,
        "selected_address": selected_address,
    })



@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "orders/detail.html", {"order": order})


from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):
    orders = request.user.orders.select_related("address").order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden

@login_required
def invoice_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if not (request.user.is_staff or order.user_id == request.user.id):
        return HttpResponseForbidden("Not allowed")
    return render(request, "orders/invoice.html", {"order": order})
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from datetime import timedelta


from django.contrib.admin.views.decorators import staff_member_required
from orders.utils import get_store_metrics

@staff_member_required
def admin_metrics(request):
    metrics = get_store_metrics()
    return render(request, "admin/metrics.html", metrics)
