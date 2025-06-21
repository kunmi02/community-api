# Community API

A robust Django REST API for community groups and posts with user authentication.

## Features

- **User Authentication**
  - JWT-based authentication
  - User registration and login
  - Profile management
  - Token refresh and verification

- **Groups**
  - Create and manage community groups
  - Public and private groups
  - Group membership with roles (member, moderator, admin)
  - Group joining and leaving functionality

- **Posts**
  - Create posts within groups
  - Like and comment on posts
  - Nested comments (replies)
  - Rich content with image support

- **Public Feed**
  - View posts from public groups
  - Personalized feed for authenticated users

## Technical Features

- Django REST Framework with viewsets and serializers
- JWT authentication with token refresh
- MySQL database support
- Environment variable configuration
- API documentation with Swagger/OpenAPI
- Pagination, filtering, and search capabilities
- Custom permissions
- Robust error handling
- Comprehensive logging

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True  # Set to False in production
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   # Database settings
   DB_NAME=community
   DB_USERNAME=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```
5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```

## API Documentation

API documentation is available at:
- `/swagger/` - Swagger UI
- `/redoc/` - ReDoc UI

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env` file
2. Configure a proper database (MySQL)
3. Set up proper `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
4. Use a production-ready web server like Gunicorn
5. Set up a reverse proxy like Nginx
6. Configure static files serving with WhiteNoise

Example production command:
```
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## License

MIT
