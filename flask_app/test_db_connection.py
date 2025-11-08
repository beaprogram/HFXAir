import pymysql
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("Testing database connection...")
print(f"DB_HOST: {os.getenv('DB_HOST', 'localhost')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'airportdb')}")
print(f"DB_USER: {os.getenv('DB_USER', 'root')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
print(f"DB_PORT: {os.getenv('DB_PORT', '3306')}")

try:
    print("\nConnecting...")
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "airportdb"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "3306")),
        connect_timeout=5
    )
    print("✓ Connected successfully!")
    
    cur = conn.cursor()
    cur.execute("SELECT VERSION();")
    version = cur.fetchone()
    print(f"✓ MariaDB/MySQL version: {version[0]}")
    
    cur.execute("SELECT COUNT(*) FROM flights;")
    count = cur.fetchone()
    print(f"✓ Flights table exists with {count[0]} rows")
    
    cur.close()
    conn.close()
    print("\n✓ Database connection test passed!")
    
except pymysql.Error as e:
    print(f"\n✗ Connection failed: {e}")
except Exception as e:
    print(f"\n✗ Error: {e}")

