# config/sitemaps.py
from django.contrib.sitemaps import Sitemap
from catalog.models import Product, Category, Brand

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    def items(self): return Product.objects.filter(is_active=True)
    def lastmod(self, obj): return obj.updated_at if hasattr(obj, "updated_at") else obj.created_at
    def location(self, obj): return obj.get_absolute_url()

from django.urls import reverse

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    def items(self): return Category.objects.all()
    def location(self, obj): return reverse("category_list", args=[obj.slug])

class BrandSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    def items(self): return Brand.objects.all()
    def location(self, obj): return reverse("brand_list", args=[obj.slug])
