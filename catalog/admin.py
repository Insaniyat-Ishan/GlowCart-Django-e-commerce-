from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, Review, ProductVariant

class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("name", "sku", "price", "stock", "is_active")
    min_num = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "brand", "category", "price", "stock", "is_active", "created_at")
    list_display_links = ("thumb", "title")
    list_filter = ("brand", "category", "is_active")
    search_fields = ("title", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "brand", "category", "short_description")}),
        ("Media", {"fields": ("image", "image_url")}),
        ("Commerce", {"fields": ("price", "stock", "is_active")}),
    )
    inlines = [VariantInline]

    def thumb(self, obj):
        url = obj.image.url if obj.image else (obj.image_url or "")
        if url:
            return format_html('<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">', url)
        return "—"
    thumb.short_description = "Image"



from .models import Category, Brand, Product, Review  # add Review import

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("product__title", "user__username", "body")
    actions = ["approve_reviews", "reject_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)

from .models import ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image", "image_url", "alt", "sort")

# and include in ProductAdmin:
inlines = [VariantInline, ProductImageInline]
