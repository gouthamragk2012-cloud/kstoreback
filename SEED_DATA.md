# Seed Data Documentation

## Overview
This document describes the seed data script that populates the KStore database with sample products and categories.

## Running the Seed Script

```bash
python seed_data.py
```

## What Gets Seeded

### Categories (5 total)
1. **Cell Phone Accessories** - Accessories for mobile phones and tablets
2. **Car Accessories** - Automotive accessories and parts
3. **Clothing** - Fashion and apparel for all
4. **Electronics** - Electronic devices and gadgets
5. **Home & Garden** - Home improvement and garden supplies

### Products (10 total)

#### Cell Phone Accessories (3 products)
- Wireless Phone Charger - $29.99 (Featured)
- Phone Case - Protective - $24.99
- USB-C Cable 6ft - $12.99

#### Car Accessories (3 products)
- Car Phone Mount - $19.99 (Featured)
- Car Air Freshener Set - $14.99
- Dash Cam HD - $79.99

#### Clothing (4 products)
- Cotton T-Shirt - Classic - $19.99 (Featured)
- Denim Jeans - Slim Fit - $49.99
- Hoodie - Pullover - $39.99
- Running Shoes - $69.99 (Featured)

## Features

- **Idempotent**: Can be run multiple times without creating duplicates (uses `ON CONFLICT DO NOTHING`)
- **Realistic Data**: Products include SKUs, descriptions, pricing, stock quantities, and brands
- **Featured Products**: Some products are marked as featured for homepage display
- **Sale Pricing**: Some products include compare_at_price for showing discounts

## Database Schema Requirements

The script expects the following tables to exist:
- `categories` (category_id, slug, name, description, is_active)
- `products` (product_id, sku, name, slug, short_description, description, price, compare_at_price, stock_quantity, category_id, brand, is_featured, is_active)

## Customization

To add more products, edit the `products` list in the `seed_products()` function. Each product should include:
- `sku`: Unique product identifier
- `name`: Product name
- `slug`: URL-friendly name
- `short_description`: Brief description
- `description`: Full description
- `price`: Product price
- `compare_at_price`: (Optional) Original price for showing discounts
- `stock_quantity`: Available inventory
- `category_id`: Reference to category
- `brand`: Brand name
- `is_featured`: (Optional) Show on homepage

## Notes

- The script uses the existing database connection pool from `db_connection.py`
- All products are set to `is_active = TRUE` by default
- Stock quantities are set to realistic values for testing
- Featured products appear on the homepage
