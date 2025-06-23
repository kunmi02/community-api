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

### Prerequisites

Before installing the Python dependencies, you need to install some system packages:

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y default-libmysqlclient-dev python3-dev build-essential
```

#### macOS
```bash
brew install mysql-client
# You may need to add mysql-client to your PATH
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
```

#### Windows
Install MySQL Connector C from the official MySQL website and add it to your PATH.

### Setup

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

## Docker Usage

This project includes Docker configuration for easy development and deployment.

### Using Docker Compose (Recommended for Development)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file with your environment variables (see Installation section).

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. The API will be available at http://localhost:8000

5. To run commands inside the container:
   ```bash
   # Run migrations
   docker-compose exec web python manage.py migrate
   
   # Create superuser
   docker-compose exec web python manage.py createsuperuser
   ```

6. To stop the containers:
   ```bash
   docker-compose down
   ```

### Using Dockerfile (Production)

1. Build the Docker image:
   ```bash
   docker build -t community-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env -e PORT=8000 community-api
   ```

3. For production deployment, consider using container orchestration services like Kubernetes or Docker Swarm.

## License

MIT
