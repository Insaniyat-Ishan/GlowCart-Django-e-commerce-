import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from orders.models import Order
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string





CURRENCY = getattr(settings, "STRIPE_CURRENCY", "usd")  # set STRIPE_CURRENCY="usd" in settings.py for USA

@login_required
def create_checkout_session(request, order_id):
    stripe.api_key = (settings.STRIPE_SECRET_KEY or "").strip()
    order = get_object_or_404(Order, id=order_id, user=request.user, status="pending")

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLIC_KEY:
        messages.error(request, "Stripe test keys are not set.")
        return redirect("order_detail", pk=order.id)

    line_items = [{
        "price_data": {
            "currency": CURRENCY,
            "product_data": {"name": f"GlowCart Order #{order.id}"},
            "unit_amount": int(order.total * 100),
        },
        "quantity": 1,
    }]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            client_reference_id=str(order.id),
            # success_url WITHOUT the placeholder; we'll read session.id from DB
            success_url=request.build_absolute_uri(f"/payments/success/?order_id={order.id}"),
            cancel_url=request.build_absolute_uri(f"/orders/{order.id}/"),
        )
        # save the session id on our Order
        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error (create): {getattr(e, 'user_message', str(e))}")
        return redirect("order_detail", pk=order.id)

    resp = HttpResponse(status=303)  # “See Other”
    resp["Location"] = session.url
    return resp


@login_required
def payment_success(request):
    stripe.api_key = (settings.STRIPE_SECRET_KEY or "").strip()

    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.stripe_session_id:
        messages.error(request, "We couldn't find your Stripe session. Please try paying again.")
        return redirect("order_detail", pk=order.id)

    try:
        # 1) Get the Checkout Session
        s = stripe.checkout.Session.retrieve(order.stripe_session_id)
        # 2) Get the PaymentIntent id
        pi_id = s.payment_intent if isinstance(s.payment_intent, str) else getattr(s.payment_intent, "id", None)
        receipt_url = ""
        # 3) Retrieve the latest charge to get a reliable receipt_url
        if pi_id:
            pi = stripe.PaymentIntent.retrieve(pi_id)
            ch_id = getattr(pi, "latest_charge", None)
            if ch_id:
                ch = stripe.Charge.retrieve(ch_id)
                receipt_url = getattr(ch, "receipt_url", "") or ""
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error (success): {getattr(e, 'user_message', str(e))}")
        return redirect("order_detail", pk=order.id)

    if getattr(s, "payment_status", None) == "paid":
        order.status = "paid"
        if not order.paid_at:
            order.paid_at = timezone.now()
        if pi_id:
            order.payment_intent_id = pi_id
        if receipt_url and not order.stripe_receipt_url:
            order.stripe_receipt_url = receipt_url
        order.save(update_fields=["status", "paid_at", "payment_intent_id", "stripe_receipt_url"])
        messages.success(request, "Payment received. Thank you!")
    else:
        messages.warning(request, f"Payment status: {getattr(s, 'payment_status', 'unknown')}")
    return redirect("order_detail", pk=order.id)
