import psycopg2
from config import Config

def update_admin_name():
    """Update admin user's name to Jeevan"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Update admin user name
        cursor.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s
            WHERE email = %s AND role = 'admin'
            RETURNING user_id, email, first_name, last_name
        """, ('Jeevan', 'Admin', 'kstoreadmin@kstore.com'))
        
        result = cursor.fetchone()
        
        if result:
            conn.commit()
            print(f"✅ Admin name updated successfully!")
            print(f"User ID: {result[0]}")
            print(f"Email: {result[1]}")
            print(f"Name: {result[2]} {result[3]}")
        else:
            print("❌ Admin user not found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    update_admin_name()
