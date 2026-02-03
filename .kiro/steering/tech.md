# Technology Stack

## Backend Stack
- **Framework**: Django 4.2.7 with Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache/Queue**: Redis 5.0.1 with Celery 5.3.4 for background tasks
- **WebSockets**: Django Channels 4.0.0 with channels-redis
- **Authentication**: JWT with djangorestframework-simplejwt
- **Web Server**: Gunicorn + Nginx (production)

## Frontend Stack
- **Framework**: React 18.2.0 with TypeScript 5.2.2
- **Build Tool**: Vite 4.5.0
- **Styling**: Tailwind CSS 3.3.5
- **State Management**: TanStack React Query 5.8.4
- **UI Components**: Headless UI, Heroicons
- **Charts**: Recharts 2.8.0
- **HTTP Client**: Axios 1.6.0

## Development Tools
- **Containerization**: Docker with Docker Compose
- **Environment Management**: python-decouple for configuration
- **CORS**: django-cors-headers for frontend integration
- **API Documentation**: Django REST Framework browsable API

## Common Commands

### Development Environment
```bash
# Start development environment
./manage.sh dev:up
# or on Windows
manage.bat dev:up

# Stop development environment
./manage.sh dev:down

# View logs
./manage.sh dev:logs [service]

# Build containers
./manage.sh dev:build
```

### Production Environment
```bash
# Start production environment
./manage.sh prod:up

# Stop production environment
./manage.sh prod:down

# Build for production
./manage.sh prod:build
```

### Database Management
```bash
# Run migrations
./manage.sh migrate [dev|prod]

# Create superuser
./manage.sh superuser [dev|prod]
```

### Testing
```bash
# Test API endpoints
./manage.sh test:api [dev|prod]

# Run backend tests
./manage.sh test:backend [dev|prod]
```

### Frontend Development
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python manage.py runserver        # Start development server
python manage.py migrate          # Run migrations
python manage.py test             # Run tests
celery -A proxyplatform worker -l info  # Start Celery worker
```

## Environment Configuration

### Development
- Uses `.env.dev` for default configuration
- SQLite database for simplicity
- Debug mode enabled
- CORS allows all origins

### Production
- Requires `.env.prod` configuration file
- PostgreSQL database required
- Debug mode disabled
- Nginx reverse proxy
- Static file serving optimized

## Key Dependencies
- **psycopg2-binary**: PostgreSQL adapter
- **beautifulsoup4 + lxml**: Web scraping capabilities
- **aiohttp**: Async HTTP requests
- **requests**: Synchronous HTTP requests
- **django-filter**: Advanced API filtering