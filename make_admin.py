"""
Script to make a user an admin
Usage: python make_admin.py <email>
"""
import sys
from db_connection import db

def make_admin(email):
    """Make a user an admin by email"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT user_id, email, first_name, last_name, role FROM users WHERE email = %s", (email.lower(),))
        user = cursor.fetchone()
        
        if not user:
            print(f"✗ User with email '{email}' not found")
            return False
        
        user_id, user_email, first_name, last_name, current_role = user
        
        if current_role == 'admin':
            print(f"✓ User {first_name} {last_name} ({user_email}) is already an admin")
            return True
        
        # Update user role to admin
        cursor.execute("UPDATE users SET role = 'admin' WHERE user_id = %s", (user_id,))
        conn.commit()
        
        print(f"✓ Successfully made {first_name} {last_name} ({user_email}) an admin!")
        print(f"  Previous role: {current_role}")
        print(f"  New role: admin")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {e}")
        return False
    finally:
        cursor.close()
        db.return_connection(conn)

def list_admins():
    """List all admin users"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, created_at
            FROM users WHERE role = 'admin'
            ORDER BY created_at DESC
        """)
        
        admins = cursor.fetchall()
        
        if not admins:
            print("No admin users found")
            return
        
        print(f"\n{'='*60}")
        print(f"Admin Users ({len(admins)} total)")
        print(f"{'='*60}")
        for admin in admins:
            print(f"ID: {admin[0]}")
            print(f"Name: {admin[2]} {admin[3]}")
            print(f"Email: {admin[1]}")
            print(f"Created: {admin[4]}")
            print("-" * 60)
        
    finally:
        cursor.close()
        db.return_connection(conn)

def main():
    """Main function"""
    db.create_pool()
    
    try:
        if len(sys.argv) < 2:
            print("Usage: python make_admin.py <email>")
            print("   or: python make_admin.py --list")
            print("\nExamples:")
            print("  python make_admin.py user@example.com")
            print("  python make_admin.py --list")
            sys.exit(1)
        
        if sys.argv[1] == '--list':
            list_admins()
        else:
            email = sys.argv[1]
            make_admin(email)
    
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    main()
