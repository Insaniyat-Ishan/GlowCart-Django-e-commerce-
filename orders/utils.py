# orders/utils.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, F, DecimalField
from .models import Order, OrderItem

def get_store_metrics():
    now = timezone.now()
    week = now - timedelta(days=7)
    month = now - timedelta(days=30)

    qs = Order.objects.all()

    data = {
        "total_orders": qs.count(),
        "total_revenue": qs.filter(status="paid").aggregate(s=Sum("total"))["s"] or 0,
        "week_revenue": qs.filter(status="paid", created_at__gte=week).aggregate(s=Sum("total"))["s"] or 0,
        "month_revenue": qs.filter(status="paid", created_at__gte=month).aggregate(s=Sum("total"))["s"] or 0,
    }

    # sum (unit_price * qty) safely (separate from other aggregates)
    top = (
        OrderItem.objects
        .values("product__title")
        .annotate(sales=Sum(F("unit_price") * F("qty"),
                            output_field=DecimalField(max_digits=12, decimal_places=2)))
        .annotate(qty=Sum("qty"))
        .order_by("-sales")[:5]
    )
    data["top_products"] = list(top)
    return data
