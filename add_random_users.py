import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cursor = conn.cursor()

# Random user data
users_data = [
    {
        'email': 'sarah.johnson@email.com',
        'password': 'password123',
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'phone': '+1-555-0101',
        'is_verified': True,
        'is_active': True
    },
    {
        'email': 'michael.chen@email.com',
        'password': 'password123',
        'first_name': 'Michael',
        'last_name': 'Chen',
        'phone': '+1-555-0102',
        'is_verified': True,
        'is_active': True
    },
    {
        'email': 'emma.williams@email.com',
        'password': 'password123',
        'first_name': 'Emma',
        'last_name': 'Williams',
        'phone': '+1-555-0103',
        'is_verified': False,
        'is_active': True
    },
    {
        'email': 'james.brown@email.com',
        'password': 'password123',
        'first_name': 'James',
        'last_name': 'Brown',
        'phone': '+1-555-0104',
        'is_verified': False,
        'is_active': True
    }
]

try:
    for user in users_data:
        # Check if user already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (user['email'],))
        if cursor.fetchone():
            print(f"User {user['email']} already exists, skipping...")
            continue
        
        # Hash password
        password_hash = generate_password_hash(user['password'])
        
        # Random last login (within last 30 days or None)
        last_login = None
        if random.choice([True, False]):
            days_ago = random.randint(1, 30)
            last_login = datetime.now() - timedelta(days=days_ago)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, phone, 
                             role, is_active, is_verified, last_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """, (
            user['email'],
            password_hash,
            user['first_name'],
            user['last_name'],
            user['phone'],
            'customer',
            user['is_active'],
            user['is_verified'],
            last_login
        ))
        
        user_id = cursor.fetchone()[0]
        print(f"✓ Created user: {user['first_name']} {user['last_name']} (ID: {user_id})")
    
    conn.commit()
    print("\n✓ Successfully added 4 random users!")
    print("\nAll users can login with password: password123")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
