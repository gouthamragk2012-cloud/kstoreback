from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from db_connection import db
from utils.response_utils import success_response, error_response, paginated_response
from utils.auth_utils import admin_required

product_bp = Blueprint('products', __name__)

@product_bp.route('', methods=['GET'])
def get_products():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    is_featured = request.args.get('is_featured')
    
    offset = (page - 1) * per_page
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Build query
        where_clauses = []
        params = []
        
        # For admin, show all products; for customers, only active ones
        # Note: This endpoint is public, so we show only active by default
        # Admin should use a different endpoint or parameter if needed
        where_clauses.append("p.is_active = TRUE")
        
        if category_id:
            where_clauses.append("p.category_id = %s")
            params.append(category_id)
        
        if search:
            where_clauses.append("(p.name ILIKE %s OR p.description ILIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if is_featured:
            where_clauses.append("p.is_featured = TRUE")
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM products p WHERE {where_sql}", params)
        total = cursor.fetchone()[0]
        
        # Get products
        cursor.execute(f"""
            SELECT p.product_id, p.sku, p.name, p.slug, p.short_description, p.price, 
                   p.compare_at_price, p.stock_quantity, p.is_featured, p.brand,
                   c.name as category_name,
                   (SELECT image_url FROM product_images WHERE product_id = p.product_id 
                    AND is_primary = TRUE LIMIT 1) as primary_image
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE {where_sql}
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'product_id': row[0],
                'sku': row[1],
                'name': row[2],
                'slug': row[3],
                'short_description': row[4],
                'price': float(row[5]),
                'compare_at_price': float(row[6]) if row[6] else None,
                'stock_quantity': row[7],
                'is_featured': row[8],
                'brand': row[9],
                'category_name': row[10],
                'primary_image': row[11]
            })
        
        return paginated_response(products, page, per_page, total)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.product_id, p.sku, p.name, p.slug, p.description, p.short_description,
                   p.price, p.compare_at_price, p.stock_quantity, p.brand, p.weight,
                   p.is_featured, p.meta_title, p.meta_description,
                   c.name as category_name, c.category_id
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s AND p.is_active = TRUE
        """, (product_id,))
        
        row = cursor.fetchone()
        if not row:
            return error_response('Product not found', 404)
        
        # Get images
        cursor.execute("""
            SELECT image_id, image_url, alt_text, is_primary, display_order
            FROM product_images WHERE product_id = %s ORDER BY display_order
        """, (product_id,))
        
        images = [{'image_id': r[0], 'image_url': r[1], 'alt_text': r[2], 
                   'is_primary': r[3], 'display_order': r[4]} for r in cursor.fetchall()]
        
        # Get variants
        cursor.execute("""
            SELECT variant_id, sku, name, price, stock_quantity, attributes
            FROM product_variants WHERE product_id = %s AND is_active = TRUE
        """, (product_id,))
        
        variants = [{'variant_id': r[0], 'sku': r[1], 'name': r[2], 
                     'price': float(r[3]) if r[3] else None, 'stock_quantity': r[4],
                     'attributes': r[5]} for r in cursor.fetchall()]
        
        product = {
            'product_id': row[0],
            'sku': row[1],
            'name': row[2],
            'slug': row[3],
            'description': row[4],
            'short_description': row[5],
            'price': float(row[6]),
            'compare_at_price': float(row[7]) if row[7] else None,
            'stock_quantity': row[8],
            'brand': row[9],
            'weight': float(row[10]) if row[10] else None,
            'is_featured': row[11],
            'meta_title': row[12],
            'meta_description': row[13],
            'category': {'name': row[14], 'category_id': row[15]} if row[14] else None,
            'images': images,
            'variants': variants
        }
        
        return success_response(product)
        
    finally:
        cursor.close()
        db.return_connection(conn)

@product_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_product():
    data = request.get_json()
    
    required = ['sku', 'name', 'slug', 'price', 'stock_quantity']
    if not all(field in data for field in required):
        return error_response('Missing required fields: ' + ', '.join(required))
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        import json
        
        # Prepare dimensions as JSON string if provided
        dimensions_json = None
        if data.get('dimensions'):
            dimensions_json = json.dumps(data['dimensions'])
        
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
            data['sku'],
            data['name'],
            data['slug'],
            data.get('description'),
            data.get('short_description'),
            data['price'],
            data.get('compare_at_price'),
            data.get('cost_price'),
            data['stock_quantity'],
            data.get('low_stock_threshold', 10),
            data.get('category_id'),
            data.get('brand'),
            data.get('weight'),
            dimensions_json,  # JSONB field as JSON string
            data.get('is_featured', False),
            data.get('is_active', True),
            data.get('meta_title'),
            data.get('meta_description')
        ))
        
        product_id = cursor.fetchone()[0]
        conn.commit()
        
        return success_response({'product_id': product_id}, 'Product created successfully', 201)
        
    except Exception as e:
        conn.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating product: {e}")
        print(f"Full traceback: {error_details}")
        print(f"Data received: {data}")
        return error_response(f'Failed to create product: {str(e)}', 500)
    finally:
        cursor.close()
        db.return_connection(conn)


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_product(product_id):
    data = request.get_json()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if product exists
        cursor.execute("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not cursor.fetchone():
            return error_response('Product not found', 404)
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = ['sku', 'name', 'slug', 'description', 'short_description', 
                         'price', 'compare_at_price', 'cost_price', 'stock_quantity', 
                         'low_stock_threshold', 'category_id', 'brand', 'weight', 
                         'dimensions', 'is_featured', 'is_active', 'meta_title', 'meta_description']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return error_response('No fields to update')
        
        # Add updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(product_id)
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
        cursor.execute(query, params)
        conn.commit()
        
        return success_response({'product_id': product_id}, 'Product updated successfully')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_product(product_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if product exists
        cursor.execute("SELECT product_id, name FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return error_response('Product not found', 404)
        
        product_name = product[1]
        
        # Soft delete - set is_active to FALSE
        cursor.execute("""
            UPDATE products 
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP 
            WHERE product_id = %s
        """, (product_id,))
        
        conn.commit()
        
        return success_response({
            'product_id': product_id,
            'name': product_name
        }, 'Product deleted successfully')
        
    except Exception as e:
        conn.rollback()
        return error_response(str(e), 500)
    finally:
        cursor.close()
        db.return_connection(conn)
