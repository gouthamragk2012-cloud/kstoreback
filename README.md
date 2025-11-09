# E-Commerce Backend API

A complete, production-ready REST API for e-commerce applications built with Flask, PostgreSQL, JWT authentication, and bcrypt encryption.

## Features

✅ **Secure Authentication**
- JWT token-based authentication
- Bcrypt password hashing
- Access & refresh tokens
- Role-based access control (Admin/Customer)

✅ **Complete E-Commerce Functionality**
- Product catalog with variants
- Shopping cart management
- Order processing with status tracking
- User reviews and ratings
- Wishlist
- Multiple addresses per user
- Coupon/discount system

✅ **Future-Proof Architecture**
- Scalable database schema
- Indexed queries for performance
- Soft deletes (ON DELETE SET NULL)
- JSONB for flexible attributes
- Pagination support
- Comprehensive error handling

## Tech Stack

- **Backend**: Flask 3.0
- **Database**: PostgreSQL 17
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: Bcrypt
- **CORS**: Flask-CORS

## Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment**
Update `.env` with your database credentials and secret keys

3. **Create database tables**
```bash
python reset_tables.py
```

4. **Run the server**
```bash
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List products (with pagination, search, filters)
- `GET /api/products/:id` - Get product details
- `POST /api/products` - Create product (Admin only)

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category (Admin only)

### Cart
- `GET /api/cart` - Get cart
- `POST /api/cart` - Add to cart
- `PUT /api/cart/:id` - Update cart item
- `DELETE /api/cart/:id` - Remove from cart
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders
- `GET /api/orders/:id` - Get order details

### User Profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/addresses` - Get addresses
- `POST /api/users/addresses` - Add address

### Wishlist
- `GET /api/wishlist` - Get wishlist
- `POST /api/wishlist/:product_id` - Add to wishlist
- `DELETE /api/wishlist/:product_id` - Remove from wishlist

### Reviews
- `GET /api/reviews/product/:id` - Get product reviews
- `POST /api/reviews` - Create review

## Testing with Postman

See `POSTMAN_GUIDE.md` for detailed API testing instructions.

### Quick Test Flow:

1. **Register**: `POST /api/auth/register`
2. **Login**: `POST /api/auth/login` (get access_token)
3. **Add Authorization header**: `Bearer YOUR_ACCESS_TOKEN`
4. **Test endpoints**: Use the token for protected routes

## Database Schema

### Core Tables
- **users** - User accounts with roles
- **products** - Product catalog
- **product_variants** - Product variations (size, color, etc.)
- **product_images** - Multiple images per product
- **categories** - Hierarchical categories
- **cart** - Shopping cart
- **orders** - Order records
- **order_items** - Order line items
- **order_status_history** - Order status tracking
- **addresses** - User addresses
- **reviews** - Product reviews
- **wishlist** - User wishlists
- **coupons** - Discount codes

## Security Features

- Password hashing with bcrypt (salt rounds: 12)
- JWT tokens with expiration
- Role-based access control
- SQL injection prevention (parameterized queries)
- CORS configuration
- Environment variable protection

## Project Structure

```
├── app.py                 # Main application
├── config.py             # Configuration
├── db_connection.py      # Database connection pool
├── requirements.txt      # Dependencies
├── .env                  # Environment variables
├── routes/
│   ├── auth_routes.py    # Authentication endpoints
│   ├── product_routes.py # Product endpoints
│   ├── cart_routes.py    # Cart endpoints
│   ├── order_routes.py   # Order endpoints
│   ├── user_routes.py    # User profile endpoints
│   ├── category_routes.py
│   ├── review_routes.py
│   └── wishlist_routes.py
└── utils/
    ├── auth_utils.py     # Auth helpers
    └── response_utils.py # Response formatters
```

## Environment Variables

```env
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

## Response Format

All API responses follow this format:

**Success:**
```json
{
  "success": true,
  "message": "Optional message",
  "data": {}
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Paginated:**
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Production Deployment

For production:
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set strong SECRET_KEY and JWT_SECRET_KEY
3. Enable HTTPS
4. Configure proper CORS origins
5. Set up database backups
6. Use environment-specific configs
7. Enable logging and monitoring

## License

MIT
