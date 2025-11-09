from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from db_connection import db
from utils.email_service import mail
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure upload settings
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # Ensure static folder exists
    os.makedirs('static/uploads', exist_ok=True)
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    mail.init_app(app)
    
    # Initialize database pool
    db.create_pool()
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.product_routes import product_bp
    from routes.category_routes import category_bp
    from routes.cart_routes import cart_bp
    from routes.order_routes import order_bp
    from routes.review_routes import review_bp
    from routes.wishlist_routes import wishlist_bp
    from routes.upload_routes import upload_bp
    from routes.verification_routes import verification_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    
    @app.route('/api/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
