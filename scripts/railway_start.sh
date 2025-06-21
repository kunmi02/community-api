#!/bin/bash
set -e

# Print environment information
echo "Starting application setup..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL environment variable is not set!"
else
    echo "DATABASE_URL is set (value hidden for security)"
fi

# Check Django configuration
echo "Checking Django configuration..."
python -c "import django; print(f'Django version: {django.get_version()}')" || echo "Failed to import Django"

# Check database connection
echo "Checking database connection..."
python scripts/check_db.py || echo "Database check failed, but continuing..."

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
exec gunicorn core.wsgi_prod:application --bind 0.0.0.0:$PORT --log-level debug
