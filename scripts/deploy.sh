#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Check if we're in production mode
if [ "$DJANGO_SETTINGS_MODULE" = "core.settings_prod" ]; then
    echo "Running in production mode"
else
    echo "Running in development mode"
    export DJANGO_SETTINGS_MODULE=core.settings
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable

# Check for errors
echo "Checking for errors..."
python manage.py check --deploy

echo "Deployment completed successfully!"
