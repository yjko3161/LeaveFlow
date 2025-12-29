import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
# mysql+pymysql://user:pass@host:port/db
if db_url and db_url.startswith('mysql'):
    parts = db_url.split('://')[1].split('@')
    creds = parts[0].split(':')
    addr = parts[1].split('/')
    host_port = addr[0].split(':')
    db_name = addr[1]
    
    conn = pymysql.connect(
        host=host_port[0],
        port=int(host_port[1]) if len(host_port) > 1 else 3306,
        user=creds[0],
        password=creds[1],
        database=db_name
    )
    
    try:
        with conn.cursor() as cursor:
            # Add card_number to users table
            print("Checking for card_number column in users table...")
            cursor.execute("SHOW COLUMNS FROM users LIKE 'card_number'")
            result = cursor.fetchone()
            if not result:
                print("Adding card_number column to users table...")
                cursor.execute("ALTER TABLE users ADD COLUMN card_number VARCHAR(20) DEFAULT NULL AFTER join_date")
                conn.commit()
                print("Success: card_number column added.")
            else:
                print("Column card_number already exists.")
    finally:
        conn.close()
else:
    print("No MySQL/MariaDB connection found in DATABASE_URL.")
