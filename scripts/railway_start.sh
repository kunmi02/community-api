#!/bin/bash
set -e

# Print environment information
echo "Starting application setup..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Ensure application code is in Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"
echo "Python path: $PYTHONPATH"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL environment variable is not set!"
else
    echo "DATABASE_URL is set (value hidden for security)"
fi

# Check Django configuration
echo "Checking Django configuration..."
python -c "import django; print(f'Django version: {django.get_version()}')" || echo "Failed to import Django"

# Wait for database to be ready
echo "Waiting for database to be ready..."
MAX_DB_RETRIES=30
DB_RETRY_COUNT=0
DB_RETRY_DELAY=5

while [ $DB_RETRY_COUNT -lt $MAX_DB_RETRIES ]; do
    echo "Attempt $((DB_RETRY_COUNT+1)) of $MAX_DB_RETRIES to connect to database..."
    if python scripts/check_db.py; then
        echo "✅ Database connection successful!"
        break
    else
        DB_RETRY_COUNT=$((DB_RETRY_COUNT+1))
        if [ $DB_RETRY_COUNT -eq $MAX_DB_RETRIES ]; then
            echo "❌ Failed to connect to database after $MAX_DB_RETRIES attempts."
            echo "Continuing anyway, as the application might work with retry logic."
        else
            echo "Database connection attempt $DB_RETRY_COUNT failed. Retrying in $DB_RETRY_DELAY seconds..."
            sleep $DB_RETRY_DELAY
        fi
    fi
done

# Run database migrations with retries
echo "Running database migrations..."
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python manage.py migrate --no-input; then
        echo "Migrations completed successfully!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        echo "Migration attempt $RETRY_COUNT failed. Retrying in 5 seconds..."
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Failed to run migrations after $MAX_RETRIES attempts."
    echo "Continuing anyway, as the database might be set up already."
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input || echo "Static file collection failed, but continuing..."

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn core.wsgi_prod:application --bind 0.0.0.0:$PORT
