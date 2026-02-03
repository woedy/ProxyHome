# Proxy Management Platform

A comprehensive web platform for managing and scraping proxies from multiple sources with Django backend and React frontend.

## Features

### 🚀 Multi-Tier Proxy Fetching
- **Premium Tier**: API-based sources (Webshare, Oxylabs, Bright Data, SmartProxy)
- **Public Tier**: Established public sources and GitHub repositories
- **Basic Tier**: Fallback sources for high volume
- **Unified Manager**: Orchestrates all tiers simultaneously

### 🌍 Advanced Proxy Features
- **Location Detection**: Complete geolocation data using multiple IP APIs
- **Protocol Support**: HTTP, SOCKS4, and SOCKS5 proxies
- **Real-time Validation**: Concurrent proxy testing and validation
- **Export Options**: JSON, TXT, and CSV formats

### 🎛️ Web Platform
- **Dashboard**: Real-time statistics and charts
- **Proxy Management**: Advanced filtering, pagination, and search
- **Credentials Manager**: Secure premium service credential storage
- **Job Monitoring**: Real-time fetch job tracking with logs
- **Settings**: Cleanup tools and system information

### 🔧 Technical Stack
- **Backend**: Django + Django REST Framework + Celery + Redis
- **Frontend**: React + TypeScript + Tailwind CSS + React Query
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deployment**: Docker Compose for Coolify

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)

### Production Deployment (Coolify)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd proxy-platform
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the platform**
   - Web Interface: http://localhost
   - API Documentation: http://localhost/api/docs/
   - Django Admin: http://localhost/admin/

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start Celery Worker**
   ```bash
   cd backend
   celery -A proxyplatform worker -l info
   ```

## Usage

### 1. Configure Premium Credentials
- Navigate to **Credentials** page
- Add API keys for premium services:
  - **Webshare**: API key
  - **Oxylabs**: Username/password
  - **Bright Data**: Username/password/endpoint
  - **SmartProxy**: Username/password

### 2. Start Proxy Fetching
- Go to **Jobs** page
- Click "Start New Job"
- Choose job type:
  - **Unified**: All tiers combined (recommended)
  - **Premium**: High-quality proxies only
  - **Public**: Free public sources
  - **Basic**: Fallback sources

### 3. Manage Proxies
- View all proxies in **Proxies** page
- Filter by type, tier, country, status
- Test selected proxies
- Export in multiple formats
- Clean up old non-working proxies

### 4. Monitor Performance
- **Dashboard** shows real-time statistics
- View proxy distribution by type and tier
- Monitor top countries and recent jobs
- Track success rates and performance metrics

## API Endpoints

### Core Endpoints
- `GET /api/proxies/` - List proxies with filtering
- `GET /api/proxies/stats/` - Get statistics
- `POST /api/proxies/test_proxies/` - Test selected proxies
- `GET /api/proxies/export/` - Export proxies
- `POST /api/jobs/start_fetch/` - Start fetch job
- `GET /api/jobs/` - List fetch jobs
- `GET /api/credentials/` - Manage credentials

### Filtering & Search
```bash
# Filter by type and tier
GET /api/proxies/?proxy_type=socks5&tier=1

# Search by country or IP
GET /api/proxies/?search=germany

# Filter working proxies only
GET /api/proxies/?is_working=true

# Pagination
GET /api/proxies/?page=2&page_size=100
```

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Premium Service Setup

#### Webshare
1. Sign up at [webshare.io](https://webshare.io)
2. Get API key from dashboard
3. Add to credentials manager

#### Oxylabs
1. Sign up at [oxylabs.io](https://oxylabs.io)
2. Get username/password from dashboard
3. Add to credentials manager

## File Structure

```
proxy-platform/
├── backend/                 # Django backend
│   ├── proxies/            # Main app
│   ├── proxyplatform/      # Django project
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # React Query hooks
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── package.json
├── docker-compose.yml      # Production deployment
├── nginx.conf             # Nginx configuration
└── README.md
```

## Standalone Scripts

The platform also includes standalone Python scripts for direct proxy fetching:

### Quick Start with Scripts
```bash
# Install dependencies
pip install -r requirements.txt

# Run unified fetcher (all tiers)
python unified_proxy_manager.py

# Run specific tiers
python premium_proxy_fetcher.py
python public_proxy_fetcher.py
python basic_proxy_fetcher.py
```

### Script Features
- **Multi-tier system**: Premium, Public, Basic sources
- **Location detection**: Country, city, region data
- **Protocol support**: HTTP, SOCKS4, SOCKS5
- **Concurrent validation**: Fast proxy testing
- **Multiple export formats**: JSON, TXT, CSV
- **Browser integration**: FoxyProxy automation

## Proxy Sources

### Premium Sources (Tier 1)
- Webshare API
- Oxylabs API
- Bright Data API
- SmartProxy API

### Public Sources (Tier 2)
- ProxyList.geonode.com
- GitHub proxy repositories
- Free proxy APIs
- Public proxy lists

### Basic Sources (Tier 3)
- Fallback free sources
- Scraped proxy lists
- Community sources

## Performance

- **Concurrent Processing**: Up to 100 workers for validation
- **Real-time Updates**: WebSocket support for live job monitoring
- **Efficient Storage**: Optimized database indexes
- **Caching**: Redis caching for improved performance
- **Background Jobs**: Celery for async processing

## Security

**Safe for development:**
- Non-sensitive API testing
- Geo-location testing
- Rate limiting simulation
- Web scraping practice

**Never use for:**
- Production applications with sensitive data
- Authentication or personal information
- Financial or healthcare data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the API documentation at `/api/docs/`
2. Review the logs in the Jobs section
3. Check Docker container logs
4. Open an issue on GitHub