"""
Script to create a default admin user
"""
from db_connection import db
from utils.auth_utils import hash_password

def create_admin_user():
    """Create admin user with predefined credentials"""
    
    email = "kstoreadmin@kstore.com"
    password = "@1234567"
    first_name = "KStore"
    last_name = "Admin"
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT user_id, email, role FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id, user_email, role = existing_user
            if role == 'admin':
                print(f"✓ Admin user already exists: {user_email}")
                print(f"  User ID: {user_id}")
                print(f"  Role: {role}")
                return True
            else:
                # Update existing user to admin
                cursor.execute("UPDATE users SET role = 'admin' WHERE user_id = %s", (user_id,))
                conn.commit()
                print(f"✓ Updated existing user to admin: {user_email}")
                print(f"  User ID: {user_id}")
                return True
        
        # Create new admin user
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified)
            VALUES (%s, %s, %s, %s, %s, TRUE, TRUE)
            RETURNING user_id, email, first_name, last_name, role
        """, (email, password_hash, first_name, last_name, 'admin'))
        
        user = cursor.fetchone()
        conn.commit()
        
        print("=" * 60)
        print("✓ Admin user created successfully!")
        print("=" * 60)
        print(f"User ID:    {user[0]}")
        print(f"Email:      {user[1]}")
        print(f"Name:       {user[2]} {user[3]}")
        print(f"Role:       {user[4]}")
        print(f"Password:   @1234567")
        print("=" * 60)
        print("\nLogin credentials:")
        print(f"  Email:    kstoreadmin@kstore.com")
        print(f"  Password: @1234567")
        print("\nAccess admin dashboard at: http://localhost:3001/admin")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating admin user: {e}")
        return False
    finally:
        cursor.close()
        db.return_connection(conn)

def main():
    """Main function"""
    print("Creating admin user...")
    db.create_pool()
    
    try:
        create_admin_user()
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    main()
