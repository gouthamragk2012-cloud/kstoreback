# API Testing Guide - Postman

## Base URL
```
http://localhost:5000/api
```

## Authentication Flow

### 1. Register a New User
**POST** `/auth/register`

Body (JSON):
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

Response includes `access_token` and `refresh_token`

### 2. Login
**POST** `/auth/login`

Body (JSON):
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 3. Get Current User
**GET** `/auth/me`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Products

### Get All Products
**GET** `/products?page=1&per_page=20&search=shirt&category_id=1`

### Get Single Product
**GET** `/products/1`

### Create Product (Admin Only)
**POST** `/products`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "sku": "PROD-001",
  "name": "Product Name",
  "slug": "product-name",
  "description": "Product description",
  "short_description": "Short desc",
  "price": 29.99,
  "compare_at_price": 39.99,
  "stock_quantity": 100,
  "category_id": 1,
  "brand": "Brand Name"
}
```

## Categories

### Get All Categories
**GET** `/categories`

### Create Category (Admin Only)
**POST** `/categories`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "name": "Electronics",
  "slug": "electronics",
  "description": "Electronic items",
  "display_order": 1
}
```

## Cart

### Get Cart
**GET** `/cart`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Add to Cart
**POST** `/cart`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "product_id": 1,
  "variant_id": null,
  "quantity": 2
}
```

### Update Cart Item
**PUT** `/cart/1`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "quantity": 3
}
```

### Remove from Cart
**DELETE** `/cart/1`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Clear Cart
**DELETE** `/cart/clear`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Orders

### Create Order
**POST** `/orders`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "shipping_address_id": 1,
  "billing_address_id": 1,
  "payment_method": "credit_card",
  "shipping_method": "standard",
  "shipping_cost": 5.99,
  "tax_amount": 2.50
}
```

### Get My Orders
**GET** `/orders?page=1&per_page=10`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Get Order Details
**GET** `/orders/1`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## User Profile

### Update Profile
**PUT** `/users/profile`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

### Get Addresses
**GET** `/users/addresses`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Add Address
**POST** `/users/addresses`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "address_type": "shipping",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "address_line2": "Apt 4B",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "is_default": true
}
```

## Wishlist

### Get Wishlist
**GET** `/wishlist`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Add to Wishlist
**POST** `/wishlist/1`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Remove from Wishlist
**DELETE** `/wishlist/1`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Reviews

### Get Product Reviews
**GET** `/reviews/product/1`

### Create Review
**POST** `/reviews`

Headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Body (JSON):
```json
{
  "product_id": 1,
  "rating": 5,
  "title": "Great product!",
  "comment": "I love this product. Highly recommended!"
}
```

## Notes

1. All protected endpoints require `Authorization: Bearer YOUR_ACCESS_TOKEN` header
2. Access tokens expire after 1 hour
3. Use `/auth/refresh` with refresh token to get new access token
4. Admin endpoints require user role to be 'admin'
5. All responses follow format:
   ```json
   {
     "success": true,
     "message": "Optional message",
     "data": {}
   }
   ```
