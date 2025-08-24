# catalog/management/commands/seed_demo.py
from django.core.management.base import BaseCommand
from catalog.models import Brand, Category, Product
from decimal import Decimal
import random

BRANDS = ["Glowify", "PureSkin Labs", "HairBloom", "AquaDerm", "SilkStrands"]
CATEGORIES = ["Cleansers", "Serums", "Moisturizers", "Sunscreens", "Hair Treatments", "Shampoo", "Conditioner"]

IMG = "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?q=80&w=1200&auto=format&fit=crop"

class Command(BaseCommand):
    help = "Seed demo brands, categories, and products"

    def handle(self, *args, **kwargs):
        brands = [Brand.objects.get_or_create(name=b)[0] for b in BRANDS]
        cats = [Category.objects.get_or_create(name=c)[0] for c in CATEGORIES]

        created = 0
        for i in range(24):
            brand = random.choice(brands)
            category = random.choice(cats)
            title = f"{brand.name} {category.name[:-1]} #{i+1}" if category.name.endswith("s") else f"{brand.name} {category.name} #{i+1}"
            price = Decimal(random.choice([9.99, 12.50, 14.99, 19.99, 24.50, 29.99, 34.99]))
            stock = random.randint(5, 50)
            Product.objects.get_or_create(
                title=title,
                brand=brand,
                category=category,
                defaults={
                    "short_description": f"High‑quality {category.name.lower()} for daily use.",
                    "price": price,
                    "stock": stock,
                    "image_url": IMG,
                    "is_active": True,
                },
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded ~{created} products (idempotent)."))
