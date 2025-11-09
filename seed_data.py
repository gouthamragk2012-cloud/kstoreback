"""
Seed script to populate the database with sample products
"""
from db_connection import db
from datetime import datetime

def seed_categories():
    """Create product categories"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    categories = [
        ('cell-phone-accessories', 'Cell Phone Accessories', 'Accessories for mobile phones and tablets'),
        ('car-accessories', 'Car Accessories', 'Automotive accessories and parts'),
        ('clothing', 'Clothing', 'Fashion and apparel for all'),
        ('electronics', 'Electronics', 'Electronic devices and gadgets'),
        ('home-garden', 'Home & Garden', 'Home improvement and garden supplies')
    ]
    
    try:
        for slug, name, description in categories:
            cursor.execute("""
                INSERT INTO categories (slug, name, description, is_active)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (slug) DO NOTHING
            """, (slug, name, description))
        
        conn.commit()
        print("✓ Categories seeded successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding categories: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)

def seed_products():
    """Create sample products"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Get category IDs
        cursor.execute("SELECT category_id, slug FROM categories")
        categories = {row[1]: row[0] for row in cursor.fetchall()}
        
        products = [
            # Cell Phone Accessories
            {
                'sku': 'CPA-001',
                'name': 'Wireless Phone Charger',
                'slug': 'wireless-phone-charger',
                'short_description': 'Fast wireless charging pad for all Qi-enabled devices',
                'description': 'Premium wireless charging pad with 15W fast charging capability. Compatible with iPhone, Samsung, and all Qi-enabled devices.',
                'price': 29.99,
                'compare_at_price': 39.99,
                'stock_quantity': 150,
                'category_id': categories.get('cell-phone-accessories'),
                'brand': 'TechCharge',
                'is_featured': True
            },
            {
                'sku': 'CPA-002',
                'name': 'Phone Case - Protective',
                'slug': 'protective-phone-case',
                'short_description': 'Military-grade drop protection phone case',
                'description': 'Ultra-protective case with military-grade drop protection. Raised edges protect screen and camera.',
                'price': 24.99,
                'stock_quantity': 200,
                'category_id': categories.get('cell-phone-accessories'),
                'brand': 'ShieldCase'
            },
            {
                'sku': 'CPA-003',
                'name': 'USB-C Cable 6ft',
                'slug': 'usb-c-cable-6ft',
                'short_description': 'Durable braided USB-C charging cable',
                'description': 'Premium braided USB-C cable with fast charging support. 6ft length for convenience.',
                'price': 12.99,
                'stock_quantity': 300,
                'category_id': categories.get('cell-phone-accessories'),
                'brand': 'CableMax'
            },
            
            # Car Accessories
            {
                'sku': 'CAR-001',
                'name': 'Car Phone Mount',
                'slug': 'car-phone-mount',
                'short_description': 'Magnetic dashboard phone holder',
                'description': 'Strong magnetic car mount with 360-degree rotation. Easy one-hand operation.',
                'price': 19.99,
                'compare_at_price': 29.99,
                'stock_quantity': 120,
                'category_id': categories.get('car-accessories'),
                'brand': 'AutoGrip',
                'is_featured': True
            },
            {
                'sku': 'CAR-002',
                'name': 'Car Air Freshener Set',
                'slug': 'car-air-freshener-set',
                'short_description': 'Premium scented car air fresheners - 5 pack',
                'description': 'Long-lasting air fresheners with natural essential oils. Pack of 5 different scents.',
                'price': 14.99,
                'stock_quantity': 180,
                'category_id': categories.get('car-accessories'),
                'brand': 'FreshDrive'
            },
            {
                'sku': 'CAR-003',
                'name': 'Dash Cam HD',
                'slug': 'dash-cam-hd',
                'short_description': '1080p HD dashboard camera with night vision',
                'description': 'Full HD dash cam with loop recording, G-sensor, and night vision. Includes 32GB SD card.',
                'price': 79.99,
                'compare_at_price': 99.99,
                'stock_quantity': 75,
                'category_id': categories.get('car-accessories'),
                'brand': 'RoadWatch'
            },
            
            # Clothing
            {
                'sku': 'CLO-001',
                'name': 'Cotton T-Shirt - Classic',
                'slug': 'cotton-tshirt-classic',
                'short_description': '100% organic cotton t-shirt',
                'description': 'Premium quality organic cotton t-shirt. Soft, breathable, and durable. Available in multiple colors.',
                'price': 19.99,
                'stock_quantity': 250,
                'category_id': categories.get('clothing'),
                'brand': 'ComfortWear',
                'is_featured': True
            },
            {
                'sku': 'CLO-002',
                'name': 'Denim Jeans - Slim Fit',
                'slug': 'denim-jeans-slim-fit',
                'short_description': 'Classic slim fit denim jeans',
                'description': 'Premium denim jeans with stretch fabric for comfort. Classic 5-pocket design.',
                'price': 49.99,
                'compare_at_price': 69.99,
                'stock_quantity': 150,
                'category_id': categories.get('clothing'),
                'brand': 'DenimCo'
            },
            {
                'sku': 'CLO-003',
                'name': 'Hoodie - Pullover',
                'slug': 'hoodie-pullover',
                'short_description': 'Comfortable fleece pullover hoodie',
                'description': 'Soft fleece hoodie with kangaroo pocket. Perfect for casual wear and layering.',
                'price': 39.99,
                'stock_quantity': 180,
                'category_id': categories.get('clothing'),
                'brand': 'CozyWear'
            },
            {
                'sku': 'CLO-004',
                'name': 'Running Shoes',
                'slug': 'running-shoes',
                'short_description': 'Lightweight athletic running shoes',
                'description': 'Breathable mesh running shoes with cushioned sole. Perfect for running and gym workouts.',
                'price': 69.99,
                'compare_at_price': 89.99,
                'stock_quantity': 100,
                'category_id': categories.get('clothing'),
                'brand': 'SportFit',
                'is_featured': True
            }
        ]
        
        for product in products:
            cursor.execute("""
                INSERT INTO products (
                    sku, name, slug, short_description, description, price,
                    compare_at_price, stock_quantity, category_id, brand, is_featured, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (sku) DO NOTHING
            """, (
                product['sku'],
                product['name'],
                product['slug'],
                product['short_description'],
                product['description'],
                product['price'],
                product.get('compare_at_price'),
                product['stock_quantity'],
                product['category_id'],
                product['brand'],
                product.get('is_featured', False)
            ))
        
        conn.commit()
        print(f"✓ {len(products)} products seeded successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error seeding products: {e}")
        raise
    finally:
        cursor.close()
        db.return_connection(conn)

def main():
    """Run all seed functions"""
    print("Starting database seeding...")
    db.create_pool()
    
    try:
        seed_categories()
        seed_products()
        print("\n✓ Database seeding completed successfully!")
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}")
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    main()
