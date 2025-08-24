# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from .sitemaps import ProductSitemap, CategorySitemap, BrandSitemap

admin.site.site_header = "GlowCart Admin"
admin.site.site_title = "GlowCart Admin"
admin.site.index_title = "Dashboard"

sitemaps = {
    "products": ProductSitemap,
    "categories": CategorySitemap,
    "brands": BrandSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("catalog.urls")),
    path("", include("cart.urls")), 
    path("", include("accounts.urls")),
    path("", include("orders.urls")),
    path("", include("wishlist.urls")),
    path("", include("payments.urls")),  # ← add

    # ✅ added sitemap + robots
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
