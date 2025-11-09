from db_connection import db

def test_connection():
    """Test the database connection"""
    db.create_pool()
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        db.return_connection(conn)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    test_connection()
