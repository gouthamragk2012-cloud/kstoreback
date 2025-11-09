import psycopg2
from dotenv import load_dotenv
import os
import sys

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python delete_customer_by_email.py <email>")
    print("Example: python delete_customer_by_email.py user@example.com")
    sys.exit(1)

email_to_delete = sys.argv[1].lower().strip()

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
    # Find user by exact email (ONLY customers)
    cursor.execute("""
        SELECT user_id, email, first_name, last_name, role 
        FROM users 
        WHERE email = %s AND role = 'customer'
    """, (email_to_delete,))
    
    user = cursor.fetchone()
    
    if not user:
        print(f"\n❌ No customer found with email: {email_to_delete}")
        print("Note: Admin users cannot be deleted with this script for safety.")
        
        # Check if it's an admin
        cursor.execute("SELECT role FROM users WHERE email = %s", (email_to_delete,))
        admin_check = cursor.fetchone()
        if admin_check and admin_check[0] == 'admin':
            print(f"⚠️  This email belongs to an ADMIN user and is protected.")
    else:
        user_id, email, first_name, last_name, role = user
        
        print(f"\n📋 Found customer:")
        print(f"  ID: {user_id}")
        print(f"  Email: {email}")
        print(f"  Name: {first_name} {last_name}")
        print(f"  Role: {role}")
        
        confirm = input(f"\n⚠️  Are you sure you want to delete this customer? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled.")
            sys.exit(0)
        
        print("\n🗑️  Deleting customer data...")
        
        # Delete related data first (foreign key constraints)
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
        
        conn.commit()
        print(f"\n✅ Successfully deleted customer: {first_name} {last_name} ({email})")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
