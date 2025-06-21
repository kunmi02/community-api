#!/usr/bin/env python
"""
Database connection checker script for Railway deployment.
This script attempts to connect to the database using the DATABASE_URL
environment variable and reports any issues.
"""

import os
import sys
import time
import django
import MySQLdb
from urllib.parse import urlparse

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_prod")

def main():
    print("Database Connection Checker")
    print("--------------------------")
    
    # Check for various database configuration options
    db_url = os.environ.get('DATABASE_URL')
    mysql_url = os.environ.get('MYSQL_URL')
    mysql_host = os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST')
    mysql_port = os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT') or '3306'
    mysql_user = os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER') or os.environ.get('MYSQL_USERNAME')
    mysql_password = os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD')
    mysql_database = os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQL_DB')
    
    # Print available configuration
    print(f"DATABASE_URL: {'Available' if db_url else 'Not set'}")
    print(f"MYSQL_URL: {'Available' if mysql_url else 'Not set'}")
    print(f"MySQL direct config: HOST={mysql_host}, DB={mysql_database}, USER={'Set' if mysql_user else 'Not set'}")
    
    # Construct a URL if we have direct MySQL variables but no URL
    if not db_url and not mysql_url and mysql_host and mysql_user and mysql_password and mysql_database:
        db_url = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        print("Constructed database URL from individual MySQL environment variables")
    
    # Check if we have any database configuration
    if not db_url and not mysql_url:
        print("ERROR: No database configuration found in environment variables!")
        return 1
    
    # Use the first available URL
    connection_url = db_url or mysql_url
    
    # Parse and sanitize the URL for display (hide password)
    parsed = urlparse(connection_url)
    safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"Using database URL: {safe_url}")
    
    # Initialize Django
    try:
        django.setup()
    except Exception as e:
        print(f"Failed to initialize Django: {e}")
        return 1
    
    # Try to connect to the database
    try:
        conn = MySQLdb.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            passwd=parsed.password,
            db=parsed.path.strip('/'),
        )
        
        cursor = conn.cursor()
        
        # Get MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"Connected to MySQL server version: {version}")
        
        # Get character set
        cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
        charset = cursor.fetchone()[1]
        print(f"Database character set: {charset}")
        
        # Get SQL mode
        cursor.execute("SELECT @@sql_mode")
        sql_mode = cursor.fetchone()[0]
        print(f"SQL mode: {sql_mode}")
        
        # Check if STRICT_TRANS_TABLES is in the SQL mode
        if 'STRICT_TRANS_TABLES' not in sql_mode:
            print("WARNING: STRICT_TRANS_TABLES is not in SQL mode. Django requires this for proper operation.")
            print("Attempting to set SQL mode with STRICT_TRANS_TABLES...")
            try:
                cursor.execute("SET SESSION sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'")
                cursor.execute("SELECT @@sql_mode")
                new_sql_mode = cursor.fetchone()[0]
                print(f"Updated SQL mode: {new_sql_mode}")
            except Exception as e:
                print(f"Failed to set SQL mode: {e}")
        
        # Get all database variables for debugging
        print("\nImportant MySQL Variables:")
        cursor.execute("SHOW VARIABLES LIKE '%char%'")
        for var in cursor.fetchall():
            print(f"{var[0]} = {var[1]}")
            
        cursor.execute("SHOW VARIABLES LIKE '%collation%'")
        for var in cursor.fetchall():
            print(f"{var[0]} = {var[1]}")
        
        cursor.close()
        conn.close()
        
        print("\nDatabase connection successful!")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
