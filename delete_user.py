import psycopg2
from dotenv import load_dotenv
import os

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

try:
    # Find user (ONLY customers, NOT admins)
    cursor.execute("""
        SELECT user_id, email, first_name, last_name, role
        FROM users 
        WHERE (first_name ILIKE %s OR email ILIKE %s)
        AND role = 'customer'
    """, ('%jeev%', '%jeev%'))
    
    users = cursor.fetchall()
    
    if not users:
        print("No customer found with name 'jeev'")
        print("(Admin users are protected and cannot be deleted with this script)")
    else:
        print(f"\nFound {len(users)} customer(s):")
        for user in users:
            print(f"  - ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}, Role: {user[4]}")
        
        print("\nDeleting customer(s)...")
        
        for user in users:
            user_id = user[0]
            
            # Delete related data first (foreign key constraints) - only if tables exist
            tables_to_clean = [
                ("order_items", "order_id IN (SELECT order_id FROM orders WHERE user_id = %s)"),
                ("orders", "user_id = %s"),
                ("reviews", "user_id = %s"),
                ("wishlist", "user_id = %s"),
                ("addresses", "user_id = %s"),
            ]
            
            for table, condition in tables_to_clean:
                try:
                    cursor.execute(f"DELETE FROM {table} WHERE {condition}", (user_id,))
                except Exception as e:
                    # Table might not exist, skip
                    pass
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            
            print(f"✓ Deleted user: {user[2]} {user[3]} ({user[1]})")
        
        conn.commit()
        print("\n✓ Successfully deleted user(s)!")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
