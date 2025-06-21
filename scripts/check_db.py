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
    
    # Import database modules
    from django.db import connections
    from django.db.utils import OperationalError
    
    # Try to connect to the database
    try:
        connection = connections['default']
        connection.ensure_connection()
        print("✅ Successfully connected to the database!")
        
        # Get database info
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"Database version: {version}")
            
            cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
            charset = cursor.fetchone()[1]
            print(f"Database charset: {charset}")
            
            cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
            sql_mode = cursor.fetchone()[1]
            print(f"SQL mode: {sql_mode}")
        
        return 0
    except OperationalError as e:
        print(f"❌ Database connection error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
