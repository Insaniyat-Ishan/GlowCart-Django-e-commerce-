# GlowCart — Django E-commerce (Skincare & Haircare)

A clean e-commerce site built with **Django 5**, **Bootstrap 5**, and **Stripe**.  
It includes product browsing, variants, cart & coupons, checkout (COD + Stripe), wishlist, reviews (with moderation), shipping methods, invoices, search autocomplete, and staff metrics.

### Live Demo (optional)
> Add an ngrok/Render/railway link here when you deploy.

---

## ✨ Features

- **Product catalog**: categories, brands, product variants (size/shade), stock tracking, gallery thumbnails.
- **Filtering & sort**: search, category/brand filters, price range, newest/price sort, pagination.
- **Cart & coupons**: add/remove, quantity update, coupon codes, order totals.
- **Wishlist**: heart toggle from product/list pages + `/wishlist/` page + navbar counter.
- **Checkout**:
  - Shipping address management (default address).
  - **Shipping methods** (Standard/Express) with live totals.
  - **Cash on Delivery** or **Stripe Checkout** (test keys).
- **Orders**: detail page, printable **Invoice**, payment status, Stripe receipt link.
- **Reviews**: user reviews with rating (moderation via admin, only approved show).
- **SEO**: sitemap + robots, OpenGraph/Twitter meta on product pages.
- **Search autocomplete**: JSON API + dropdown suggestions in the navbar.
- **Admin/Staff**:
  - `/dashboard/metrics/` revenue & top product stats (staff-only).
  - **Profile** page shows a mini metrics card for staff users.
- **UI**: polished login/register screens, hero/featured tiles, consistent product card design.
- **Extras**: `money` template filter, cart/wishlist context processors, “recently viewed”.

---

## 🧰 Tech Stack

- Python 3.12, Django 5.2
- Bootstrap 5
- SQLite (dev) — switchable to Postgres/MySQL
- Stripe (test mode)

---

## 🚀 Quickstart

```bash
# 1) clone
git clone https://github.com/YOUR_USERNAME/glowcart.git
cd glowcart

# 2) virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate

# 3) deps
pip install -r requirements.txt

# 4) environment
copy .env.example .env
# fill in your keys in .env (dev safe)

# 5) DB & superuser
python manage.py migrate
python manage.py createsuperuser

# 6) run
python manage.py runserver
