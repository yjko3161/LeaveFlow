import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('DATABASE_URL')
print(f"Testing connection to: {url}")

try:
    engine = create_engine(url, connect_args={'connect_timeout': 10})
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection Successful! Result: {result.fetchone()}")
        
        result2 = conn.execute(text("SELECT count(*) FROM users"))
        print(f"User Count: {result2.fetchone()[0]}")
except Exception as e:
    print(f"Connection FAILED: {e}")
