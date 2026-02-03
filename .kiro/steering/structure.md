# Project Structure

## Root Directory Layout
```
proxy-platform/
├── backend/                 # Django backend application
├── frontend/               # React frontend application
├── .kiro/                  # Kiro configuration and steering
├── proxy_data/             # Generated proxy data files
├── logs/                   # Application logs
├── docker-compose*.yml     # Docker orchestration
├── nginx.conf             # Nginx configuration
├── manage.sh/.bat         # Management scripts
└── *_proxy_fetcher.py     # Standalone proxy fetchers
```

## Backend Structure (`backend/`)
```
backend/
├── proxyplatform/         # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # URL routing
│   ├── asgi.py           # ASGI application
│   └── wsgi.py           # WSGI application
├── proxies/              # Main application
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App URL patterns
│   ├── tasks.py          # Celery tasks
│   ├── consumers.py      # WebSocket consumers
│   ├── filters.py        # API filters
│   └── migrations/       # Database migrations
├── accounts/             # User management
│   ├── models.py         # Custom user model
│   ├── views.py          # Auth views
│   └── serializers.py    # Auth serializers
├── static/               # Static files (collected)
├── requirements.txt      # Python dependencies
└── manage.py            # Django management
```

## Frontend Structure (`frontend/`)
```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx    # Main layout wrapper
│   │   ├── LoadingSpinner.tsx
│   │   ├── Pagination.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── ProxyList.tsx
│   │   ├── FetchJobs.tsx
│   │   ├── Login.tsx
│   │   └── Settings.tsx
│   ├── hooks/           # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useProxies.ts
│   │   └── useJobs.ts
│   ├── services/        # API service layer
│   │   └── api.ts       # Axios configuration
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── dist/                # Build output
├── package.json         # Node dependencies
├── vite.config.ts       # Vite configuration
└── tailwind.config.js   # Tailwind CSS config
```

## Configuration Files
- **Docker Compose**: Separate files for dev/prod environments
- **Environment**: `.env.dev`, `.env.prod.example` for configuration
- **Nginx**: `nginx.conf` for production reverse proxy
- **Management**: `manage.sh`/`manage.bat` for common operations

## Data Directories
- **proxy_data/**: Generated proxy files and exports
- **logs/**: Application and system logs
- **static/**: Collected Django static files (production)

## Key Architectural Patterns

### Backend Patterns
- **Django Apps**: Modular app structure (proxies, accounts)
- **DRF ViewSets**: RESTful API endpoints with filtering
- **Celery Tasks**: Background job processing
- **WebSocket Consumers**: Real-time updates
- **Custom User Model**: Extended authentication

### Frontend Patterns
- **Component-based**: Reusable UI components
- **Custom Hooks**: Business logic abstraction
- **Service Layer**: Centralized API communication
- **Protected Routes**: Authentication-based routing
- **React Query**: Server state management

### File Naming Conventions
- **Backend**: Snake_case for Python files
- **Frontend**: PascalCase for components, camelCase for utilities
- **Configuration**: Kebab-case for config files
- **Database**: Snake_case for models and fields

### Import Patterns
- **Absolute imports**: Preferred in both frontend and backend
- **Barrel exports**: Used in frontend types and services
- **Django imports**: Follow Django conventions for apps