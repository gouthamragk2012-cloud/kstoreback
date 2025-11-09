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
    # Add verification columns
    cursor.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS verification_token VARCHAR(6),
        ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP;
    """)
    
    conn.commit()
    print("✓ Successfully added verification columns to users table!")
    
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
