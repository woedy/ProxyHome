@echo off
setlocal enabledelayedexpansion

REM Proxy Platform Management Script for Windows

set "command=%1"
set "option=%2"

if "%command%"=="" set "command=help"

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)
goto :eof

REM Function to create necessary directories
:create_directories
echo [INFO] Creating necessary directories...
if not exist "proxy_data" mkdir proxy_data
if not exist "logs" mkdir logs
echo [SUCCESS] Directories created
goto :eof

REM Development environment
:dev_up
echo [INFO] Starting development environment...
call :check_docker
call :create_directories

if not exist ".env" (
    copy ".env.dev" ".env" >nul
    echo [WARNING] Created .env file from .env.dev template
)

docker-compose -f docker-compose.dev.yml up -d
echo [SUCCESS] Development environment started
echo [INFO] Frontend: http://localhost:3000
echo [INFO] Backend API: http://localhost:8000/api
echo [INFO] Django Admin: http://localhost:8000/admin
goto :eof

:dev_down
echo [INFO] Stopping development environment...
docker-compose -f docker-compose.dev.yml down
echo [SUCCESS] Development environment stopped
goto :eof

:dev_logs
docker-compose -f docker-compose.dev.yml logs -f %option%
goto :eof

:dev_build
echo [INFO] Building development environment...
docker-compose -f docker-compose.dev.yml build --no-cache
echo [SUCCESS] Development environment built
goto :eof

REM Production environment
:prod_up
echo [INFO] Starting production environment...
call :check_docker
call :create_directories

if not exist ".env.prod" (
    echo [ERROR] Production environment file .env.prod not found
    echo [INFO] Please copy .env.prod.example to .env.prod and configure it
    exit /b 1
)

echo [INFO] Building frontend...
cd frontend && npm run build && cd ..

docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
echo [SUCCESS] Production environment started
echo [INFO] Application: http://localhost
goto :eof

:prod_down
echo [INFO] Stopping production environment...
docker-compose -f docker-compose.prod.yml down
echo [SUCCESS] Production environment stopped
goto :eof

:prod_logs
docker-compose -f docker-compose.prod.yml logs -f %option%
goto :eof

:prod_build
echo [INFO] Building production environment...
cd frontend && npm run build && cd ..
docker-compose -f docker-compose.prod.yml build --no-cache
echo [SUCCESS] Production environment built
goto :eof

REM Database management
:migrate
set "env=%option%"
if "%env%"=="" set "env=dev"

if "%env%"=="prod" (
    set "compose_file=docker-compose.prod.yml"
    set "env_file=--env-file .env.prod"
) else (
    set "compose_file=docker-compose.dev.yml"
    set "env_file="
)

echo [INFO] Running database migrations...
docker-compose -f %compose_file% %env_file% exec backend python manage.py migrate
echo [SUCCESS] Database migrations completed
goto :eof

:superuser
set "env=%option%"
if "%env%"=="" set "env=dev"

if "%env%"=="prod" (
    set "compose_file=docker-compose.prod.yml"
    set "env_file=--env-file .env.prod"
) else (
    set "compose_file=docker-compose.dev.yml"
    set "env_file="
)

echo [INFO] Creating superuser...
docker-compose -f %compose_file% %env_file% exec backend python manage.py createsuperuser
goto :eof

REM Testing
:test_api
set "env=%option%"
if "%env%"=="" set "env=dev"

if "%env%"=="prod" (
    set "base_url=http://localhost"
) else (
    set "base_url=http://localhost:8000"
)

echo [INFO] Testing API endpoints...

curl -f "%base_url%/api/health/" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Health endpoint: FAILED
) else (
    echo [SUCCESS] Health endpoint: OK
)

curl -f "%base_url%/api/proxies/stats/" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Stats endpoint: FAILED
) else (
    echo [SUCCESS] Stats endpoint: OK
)

curl -f "%base_url%/api/proxies/" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Proxies endpoint: FAILED
) else (
    echo [SUCCESS] Proxies endpoint: OK
)
goto :eof

REM Cleanup
:cleanup
echo [INFO] Cleaning up Docker resources...
docker system prune -f
docker volume prune -f
echo [SUCCESS] Cleanup completed
goto :eof

REM Help function
:show_help
echo Proxy Platform Management Script
echo.
echo Usage: %0 ^<command^> [options]
echo.
echo Development Commands:
echo   dev:up          Start development environment
echo   dev:down        Stop development environment
echo   dev:build       Build development environment
echo   dev:logs [service]  Show logs for development environment
echo.
echo Production Commands:
echo   prod:up         Start production environment
echo   prod:down       Stop production environment
echo   prod:build      Build production environment
echo   prod:logs [service]  Show logs for production environment
echo.
echo Database Commands:
echo   migrate [env]   Run database migrations (env: dev^|prod, default: dev)
echo   superuser [env] Create superuser (env: dev^|prod, default: dev)
echo.
echo Testing Commands:
echo   test:api [env]      Test API endpoints
echo.
echo Utility Commands:
echo   cleanup         Clean up Docker resources
echo   help            Show this help message
echo.
echo Examples:
echo   %0 dev:up                 # Start development environment
echo   %0 prod:up                # Start production environment
echo   %0 migrate prod           # Run migrations in production
echo   %0 dev:logs backend       # Show backend logs in development
echo   %0 test:api dev           # Test API in development environment
goto :eof

REM Main command handler
if "%command%"=="dev:up" goto dev_up
if "%command%"=="dev:down" goto dev_down
if "%command%"=="dev:build" goto dev_build
if "%command%"=="dev:logs" goto dev_logs
if "%command%"=="prod:up" goto prod_up
if "%command%"=="prod:down" goto prod_down
if "%command%"=="prod:build" goto prod_build
if "%command%"=="prod:logs" goto prod_logs
if "%command%"=="migrate" goto migrate
if "%command%"=="superuser" goto superuser
if "%command%"=="test:api" goto test_api
if "%command%"=="cleanup" goto cleanup
if "%command%"=="help" goto show_help
goto show_help