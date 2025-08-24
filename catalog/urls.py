# catalog/urls.py
from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, BrandListView
from .views import search_suggest

from .views import ProductListView, ProductDetailView, CategoryListView, BrandListView, add_review
urlpatterns = [
    path("shop/", ProductListView.as_view(), name="product_list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("product/<slug:slug>/review/", add_review, name="add_review"),  # ← new
    path("category/<slug:slug>/", CategoryListView.as_view(), name="category_list"),
    path("brand/<slug:slug>/", BrandListView.as_view(), name="brand_list"),
    path("api/suggest/", search_suggest, name="search_suggest"),
]
