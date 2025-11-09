"""
Test script to create a product directly
"""
from db_connection import db
import json

def test_create():
    db.create_pool()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Test data
        test_product = {
            'sku': 'TEST-001',
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'short_description': 'Test short desc',
            'price': 29.99,
            'compare_at_price': 39.99,
            'cost_price': 15.00,
            'stock_quantity': 100,
            'low_stock_threshold': 10,
            'category_id': 1,
            'brand': 'TestBrand',
            'weight': 0.5,
            'dimensions': json.dumps({'length': '10', 'width': '5', 'height': '3', 'unit': 'cm'}),
            'is_featured': False,
            'is_active': True,
            'meta_title': 'Test Product',
            'meta_description': 'Test meta'
        }
        
        cursor.execute("""
            INSERT INTO products (
                sku, name, slug, description, short_description, price,
                compare_at_price, cost_price, stock_quantity, low_stock_threshold,
                category_id, brand, weight, dimensions, is_featured, is_active,
                meta_title, meta_description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING product_id
        """, (
            test_product['sku'],
            test_product['name'],
            test_product['slug'],
            test_product['description'],
            test_product['short_description'],
            test_product['price'],
            test_product['compare_at_price'],
            test_product['cost_price'],
            test_product['stock_quantity'],
            test_product['low_stock_threshold'],
            test_product['category_id'],
            test_product['brand'],
            test_product['weight'],
            test_product['dimensions'],
            test_product['is_featured'],
            test_product['is_active'],
            test_product['meta_title'],
            test_product['meta_description']
        ))
        
        product_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"✓ Product created successfully! ID: {product_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        db.return_connection(conn)
        db.close_all_connections()

if __name__ == "__main__":
    test_create()
