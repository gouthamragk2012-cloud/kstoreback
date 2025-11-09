from db_connection import db

def reset_tables():
    """Drop and recreate all tables"""
    db.create_pool()
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        print("Dropping existing tables...")
        cursor.execute("""
            DROP TABLE IF EXISTS order_status_history CASCADE;
            DROP TABLE IF EXISTS wishlist CASCADE;
            DROP TABLE IF EXISTS coupons CASCADE;
            DROP TABLE IF EXISTS reviews CASCADE;
            DROP TABLE IF EXISTS cart CASCADE;
            DROP TABLE IF EXISTS order_items CASCADE;
            DROP TABLE IF EXISTS orders CASCADE;
            DROP TABLE IF EXISTS addresses CASCADE;
            DROP TABLE IF EXISTS product_images CASCADE;
            DROP TABLE IF EXISTS product_variants CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS categories CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        
        print("Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                role VARCHAR(50) DEFAULT 'customer',
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_users_email ON users(email);
            CREATE INDEX idx_users_role ON users(role);
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                parent_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
                image_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_categories_slug ON categories(slug);
            CREATE INDEX idx_categories_parent ON categories(parent_id);
        """)
        
        # Products table
        cursor.execute("""
            CREATE TABLE products (
                product_id SERIAL PRIMARY KEY,
                sku VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                short_description VARCHAR(500),
                price DECIMAL(10, 2) NOT NULL,
                compare_at_price DECIMAL(10, 2),
                cost_price DECIMAL(10, 2),
                stock_quantity INTEGER DEFAULT 0,
                low_stock_threshold INTEGER DEFAULT 10,
                category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
                brand VARCHAR(100),
                weight DECIMAL(10, 2),
                dimensions JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                is_featured BOOLEAN DEFAULT FALSE,
                meta_title VARCHAR(255),
                meta_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_products_sku ON products(sku);
            CREATE INDEX idx_products_slug ON products(slug);
            CREATE INDEX idx_products_category ON products(category_id);
            CREATE INDEX idx_products_active ON products(is_active);
            CREATE INDEX idx_products_featured ON products(is_featured);
        """)
        
        # Product images table
        cursor.execute("""
            CREATE TABLE product_images (
                image_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                image_url VARCHAR(500) NOT NULL,
                alt_text VARCHAR(255),
                is_primary BOOLEAN DEFAULT FALSE,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_product_images_product ON product_images(product_id);
        """)
        
        # Product variants table
        cursor.execute("""
            CREATE TABLE product_variants (
                variant_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                sku VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2),
                stock_quantity INTEGER DEFAULT 0,
                attributes JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_product_variants_product ON product_variants(product_id);
            CREATE INDEX idx_product_variants_sku ON product_variants(sku);
        """)
        
        # Addresses table
        cursor.execute("""
            CREATE TABLE addresses (
                address_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                address_type VARCHAR(50) DEFAULT 'shipping',
                full_name VARCHAR(200),
                phone VARCHAR(20),
                address_line1 VARCHAR(255) NOT NULL,
                address_line2 VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100),
                postal_code VARCHAR(20) NOT NULL,
                country VARCHAR(100) NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_addresses_user ON addresses(user_id);
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                tax_amount DECIMAL(10, 2) DEFAULT 0,
                shipping_cost DECIMAL(10, 2) DEFAULT 0,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                shipping_address_id INTEGER REFERENCES addresses(address_id),
                billing_address_id INTEGER REFERENCES addresses(address_id),
                payment_method VARCHAR(50),
                payment_status VARCHAR(50) DEFAULT 'pending',
                payment_transaction_id VARCHAR(255),
                shipping_method VARCHAR(100),
                tracking_number VARCHAR(100),
                notes TEXT,
                cancelled_at TIMESTAMP,
                shipped_at TIMESTAMP,
                delivered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_orders_number ON orders(order_number);
            CREATE INDEX idx_orders_user ON orders(user_id);
            CREATE INDEX idx_orders_status ON orders(status);
            CREATE INDEX idx_orders_created ON orders(created_at);
        """)
        
        # Order items table
        cursor.execute("""
            CREATE TABLE order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(product_id) ON DELETE SET NULL,
                variant_id INTEGER REFERENCES product_variants(variant_id) ON DELETE SET NULL,
                product_name VARCHAR(255) NOT NULL,
                sku VARCHAR(100),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_order_items_order ON order_items(order_id);
            CREATE INDEX idx_order_items_product ON order_items(product_id);
        """)
        
        # Cart table
        cursor.execute("""
            CREATE TABLE cart (
                cart_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                variant_id INTEGER REFERENCES product_variants(variant_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id, variant_id)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_cart_user ON cart(user_id);
        """)
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE reviews (
                review_id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE SET NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                title VARCHAR(255),
                comment TEXT,
                is_verified_purchase BOOLEAN DEFAULT FALSE,
                is_approved BOOLEAN DEFAULT TRUE,
                helpful_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_reviews_product ON reviews(product_id);
            CREATE INDEX idx_reviews_user ON reviews(user_id);
        """)
        
        # Coupons table
        cursor.execute("""
            CREATE TABLE coupons (
                coupon_id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                discount_type VARCHAR(20) NOT NULL,
                discount_value DECIMAL(10, 2) NOT NULL,
                min_purchase_amount DECIMAL(10, 2),
                max_discount_amount DECIMAL(10, 2),
                usage_limit INTEGER,
                used_count INTEGER DEFAULT 0,
                valid_from TIMESTAMP,
                valid_until TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_coupons_code ON coupons(code);
        """)
        
        # Wishlist table
        cursor.execute("""
            CREATE TABLE wishlist (
                wishlist_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_id)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_wishlist_user ON wishlist(user_id);
        """)
        
        # Order status history table
        cursor.execute("""
            CREATE TABLE order_status_history (
                history_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                status VARCHAR(50) NOT NULL,
                notes TEXT,
                created_by INTEGER REFERENCES users(user_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE INDEX idx_order_history_order ON order_status_history(order_id);
        """)
        
        conn.commit()
        print("✓ All tables created successfully with future-proof schema!")
        
        cursor.close()
        db.return_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    reset_tables()
