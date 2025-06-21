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
    
    # Check DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable is not set!")
        return 1
    
    # Parse and sanitize the URL for display (hide password)
    parsed = urlparse(db_url)
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
