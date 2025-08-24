# catalog/views.py
from django.views.generic import ListView, DetailView
from .models import Product
from django.shortcuts import get_object_or_404
from .models import Product, Category, Brand
from decimal import Decimal, InvalidOperation
from django.db.models import Avg, Count, Q

class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("brand", "category")
        q = self.request.GET.get("q", "").strip()
        cat = self.request.GET.get("category")
        br = self.request.GET.get("brand")
        pmin = self.request.GET.get("min")
        pmax = self.request.GET.get("max")
        order = self.request.GET.get("order", "new")  # new | price_asc | price_desc

        if q:
            qs = qs.filter(title__icontains=q)

        if cat:
            qs = qs.filter(category__slug=cat)

        if br:
            qs = qs.filter(brand__slug=br)

        def d(val):
            try:
                return Decimal(val)
            except (InvalidOperation, TypeError):
                return None

        dmin, dmax = d(pmin), d(pmax)
        if dmin is not None:
            qs = qs.filter(price__gte=dmin)
        if dmax is not None:
            qs = qs.filter(price__lte=dmax)

        # ✅ Annotate ratings before ordering
        qs = qs.annotate(
            rating_avg=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            rating_count=Count("reviews", filter=Q(reviews__is_approved=True)),
        )

        # ✅ Ordering
        if order == "price_asc":
            qs = qs.order_by("price", "-created_at")
        elif order == "price_desc":
            qs = qs.order_by("-price", "-created_at")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = ctx.get("page_title", "Shop")
        # For filter dropdowns
        ctx["all_categories"] = Category.objects.order_by("name")
        ctx["all_brands"] = Brand.objects.order_by("name")
        return ctx
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from .models import Product, Category, Brand, Review

from django.db.models import Avg, Count

from django.db.models import Avg, Count

class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.object

        # Reviews summary
        approved = p.reviews.filter(is_approved=True)
        agg = approved.aggregate(avg=Avg("rating"), cnt=Count("id"))
        ctx["reviews"] = approved
        ctx["rating_avg"] = (agg["avg"] or 0)
        ctx["rating_count"] = agg["cnt"] or 0

        # Variants info for template (avoid calling .filter(...) in templates)
        all_variants = p.variants.all()
        active_variants = all_variants.filter(is_active=True, stock__gt=0)
        ctx["has_variants"] = all_variants.exists()
        ctx["has_buyable_variant"] = active_variants.exists()
        ctx["all_variants"] = all_variants  # iterate safely in template
        return ctx


    

    def _push_recent(self, request, product_id: int, limit: int = 8):
        key = "recently_viewed"
        lst = request.session.get(key, [])
        lst = [pid for pid in lst if pid != product_id]
        lst.insert(0, product_id)
        request.session[key] = lst[:limit]
        request.session.modified = True


@login_required
def add_review(request, slug):
    product = Product.objects.get(slug=slug, is_active=True)
    if request.method == "POST":
        rating = int(request.POST.get("rating", "0"))
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        if rating < 1 or rating > 5:
            messages.error(request, "Please choose a rating from 1 to 5.")
            return redirect(product.get_absolute_url())
        review, _ = Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={"rating": rating, "title": title, "body": body, "is_approved": False}
        )
        messages.success(request, "Thanks! Your review is submitted for approval.")
    return redirect(product.get_absolute_url())



class CategoryListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (Product.objects.filter(is_active=True, category=self.category)
                .select_related("brand", "category"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Category: {self.category.name}"
        ctx["active_category"] = self.category
        return ctx

class BrandListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        self.brand = get_object_or_404(Brand, slug=self.kwargs["slug"])
        return (Product.objects.filter(is_active=True, brand=self.brand)
                .select_related("brand", "category"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = f"Brand: {self.brand.name}"
        ctx["active_brand"] = self.brand
        return ctx
    


from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET

@require_GET
def search_suggest(request):
    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"results": []})
    qs = (Product.objects.filter(is_active=True)
          .filter(Q(title__icontains=q)|Q(brand__name__icontains=q)|Q(category__name__icontains=q))
          .select_related("brand","category")
          .order_by("-created_at")[:8])
    results = [{"title": p.title,
                "url": p.get_absolute_url(),
                "brand": p.brand.name,
                "image": (p.image.url if p.image else p.image_url or ""),
                "price": str(p.price)} for p in qs]
    return JsonResponse({"results": results})
