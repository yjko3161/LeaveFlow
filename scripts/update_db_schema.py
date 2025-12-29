import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

def update_schema():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    if not db_url or "mysql" not in db_url:
        print("DATABASE_URL is not set for MySQL/MariaDB or is using SQLite.")
        return

    # ParseDATABASE_URL: mysql+pymysql://user:pass@host:port/dbname
    url = urlparse(db_url.replace('mysql+pymysql://', 'http://'))
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port or 3306
    dbname = url.path[1:]

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=dbname
        )
        with connection.cursor() as cursor:
            # Add stamp_path to company_info
            try:
                cursor.execute("ALTER TABLE company_info ADD COLUMN stamp_path VARCHAR(200)")
                print("Added stamp_path to company_info")
            except pymysql.err.InternalError as e:
                # 1060 is "Duplicate column name"
                if e.args[0] == 1060:
                    print("stamp_path already exists in company_info")
                else:
                    raise e

            # Add provider_stamp_path to quotes
            try:
                cursor.execute("ALTER TABLE quotes ADD COLUMN provider_stamp_path VARCHAR(200)")
                print("Added provider_stamp_path to quotes")
            except pymysql.err.InternalError as e:
                if e.args[0] == 1060:
                    print("provider_stamp_path already exists in quotes")
                else:
                    raise e
            
        connection.commit()
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    update_schema()
