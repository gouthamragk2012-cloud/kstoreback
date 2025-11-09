"""
Create support_messages table for customer support chat
"""
from db_connection import db

def create_support_table():
    # Initialize database pool
    db.create_pool()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Create support_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_messages (
                message_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                order_id INTEGER REFERENCES orders(order_id) ON DELETE SET NULL,
                message_text TEXT NOT NULL,
                sender VARCHAR(20) NOT NULL CHECK (sender IN ('customer', 'admin')),
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'replied', 'closed')),
                telegram_message_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_user_id ON support_messages(user_id);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_support_status ON support_messages(status);
        """)
        
        conn.commit()
        print("✅ Support messages table created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating table: {e}")
    finally:
        cursor.close()
        db.return_connection(conn)

if __name__ == '__main__':
    create_support_table()
