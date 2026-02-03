#!/bin/bash

# Proxy Platform Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p proxy_data logs
    print_success "Directories created"
}

# Development environment
dev_up() {
    print_status "Starting development environment..."
    check_docker
    create_directories
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.dev .env
        print_warning "Created .env file from .env.dev template"
    fi
    
    docker-compose -f docker-compose.dev.yml up -d
    print_success "Development environment started"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000/api"
    print_status "Django Admin: http://localhost:8000/admin"
}

dev_down() {
    print_status "Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
    print_success "Development environment stopped"
}

dev_logs() {
    docker-compose -f docker-compose.dev.yml logs -f "${2:-}"
}

dev_build() {
    print_status "Building development environment..."
    docker-compose -f docker-compose.dev.yml build --no-cache
    print_success "Development environment built"
}

# Production environment
prod_up() {
    print_status "Starting production environment..."
    check_docker
    create_directories
    
    # Check if production env file exists
    if [ ! -f .env.prod ]; then
        print_error "Production environment file .env.prod not found"
        print_status "Please copy .env.prod.example to .env.prod and configure it"
        exit 1
    fi
    
    # Build frontend first
    print_status "Building frontend..."
    cd frontend && npm run build && cd ..
    
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
    print_success "Production environment started"
    print_status "Application: http://localhost"
}

prod_down() {
    print_status "Stopping production environment..."
    docker-compose -f docker-compose.prod.yml down
    print_success "Production environment stopped"
}

prod_logs() {
    docker-compose -f docker-compose.prod.yml logs -f "${2:-}"
}

prod_build() {
    print_status "Building production environment..."
    cd frontend && npm run build && cd ..
    docker-compose -f docker-compose.prod.yml build --no-cache
    print_success "Production environment built"
}

# Database management
migrate() {
    ENV=${2:-dev}
    if [ "$ENV" = "prod" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE="--env-file .env.prod"
    else
        COMPOSE_FILE="docker-compose.dev.yml"
        ENV_FILE=""
    fi
    
    print_status "Running database migrations..."
    docker-compose -f $COMPOSE_FILE $ENV_FILE exec backend python manage.py migrate
    print_success "Database migrations completed"
}

create_superuser() {
    ENV=${2:-dev}
    if [ "$ENV" = "prod" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE="--env-file .env.prod"
    else
        COMPOSE_FILE="docker-compose.dev.yml"
        ENV_FILE=""
    fi
    
    print_status "Creating superuser..."
    docker-compose -f $COMPOSE_FILE $ENV_FILE exec backend python manage.py createsuperuser
}

# Testing
test_backend() {
    ENV=${2:-dev}
    if [ "$ENV" = "prod" ]; then
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE="--env-file .env.prod"
    else
        COMPOSE_FILE="docker-compose.dev.yml"
        ENV_FILE=""
    fi
    
    print_status "Running backend tests..."
    docker-compose -f $COMPOSE_FILE $ENV_FILE exec backend python manage.py test
}

test_api() {
    ENV=${2:-dev}
    if [ "$ENV" = "prod" ]; then
        BASE_URL="http://localhost"
    else
        BASE_URL="http://localhost:8000"
    fi
    
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f "$BASE_URL/api/health/" > /dev/null 2>&1; then
        print_success "Health endpoint: OK"
    else
        print_error "Health endpoint: FAILED"
    fi
    
    # Test stats endpoint
    if curl -f "$BASE_URL/api/proxies/stats/" > /dev/null 2>&1; then
        print_success "Stats endpoint: OK"
    else
        print_error "Stats endpoint: FAILED"
    fi
    
    # Test proxies endpoint
    if curl -f "$BASE_URL/api/proxies/" > /dev/null 2>&1; then
        print_success "Proxies endpoint: OK"
    else
        print_error "Proxies endpoint: FAILED"
    fi
}

# Cleanup
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed"
}

# Help function
show_help() {
    echo "Proxy Platform Management Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Development Commands:"
    echo "  dev:up          Start development environment"
    echo "  dev:down        Stop development environment"
    echo "  dev:build       Build development environment"
    echo "  dev:logs [service]  Show logs for development environment"
    echo ""
    echo "Production Commands:"
    echo "  prod:up         Start production environment"
    echo "  prod:down       Stop production environment"
    echo "  prod:build      Build production environment"
    echo "  prod:logs [service]  Show logs for production environment"
    echo ""
    echo "Database Commands:"
    echo "  migrate [env]   Run database migrations (env: dev|prod, default: dev)"
    echo "  superuser [env] Create superuser (env: dev|prod, default: dev)"
    echo ""
    echo "Testing Commands:"
    echo "  test:backend [env]  Run backend tests"
    echo "  test:api [env]      Test API endpoints"
    echo ""
    echo "Utility Commands:"
    echo "  cleanup         Clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev:up                 # Start development environment"
    echo "  $0 prod:up                # Start production environment"
    echo "  $0 migrate prod           # Run migrations in production"
    echo "  $0 dev:logs backend       # Show backend logs in development"
    echo "  $0 test:api dev           # Test API in development environment"
}

# Main command handler
case "${1:-help}" in
    "dev:up")
        dev_up
        ;;
    "dev:down")
        dev_down
        ;;
    "dev:build")
        dev_build
        ;;
    "dev:logs")
        dev_logs "$@"
        ;;
    "prod:up")
        prod_up
        ;;
    "prod:down")
        prod_down
        ;;
    "prod:build")
        prod_build
        ;;
    "prod:logs")
        prod_logs "$@"
        ;;
    "migrate")
        migrate "$@"
        ;;
    "superuser")
        create_superuser "$@"
        ;;
    "test:backend")
        test_backend "$@"
        ;;
    "test:api")
        test_api "$@"
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_help
        ;;
esac