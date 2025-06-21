#!/bin/bash

# Print environment information
echo "Starting application setup..."
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Start the application
echo "Starting Gunicorn server..."
gunicorn core.wsgi_prod:application --bind 0.0.0.0:$PORT
