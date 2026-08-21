# BharatResilience AI

**Real-Time Disaster Detection and AI-Powered Emergency Response Platform**

🛡️ An intelligent system that continuously monitors live data streams, automatically detects abnormal or dangerous events, and generates AI-powered response plans for disaster management.

## 🎯 Features

### Real-Time Detection
- **Automatic Monitoring**: Continuous ingestion and processing of real-time data feeds
- **Multiple Hazard Types**: 
  - 🌧️ Extreme Rainfall
  - 🌊 Flood Risk
  - 🌡️ Extreme Heat
  - 💧 Water Shortage
  - 🌪️ Severe Weather
  - 📍 Earthquake Events
  - ⚡ Configurable Custom Hazards

### Anomaly Detection
- **Machine Learning**: Scikit-learn Isolation Forest algorithm for unsupervised anomaly detection
- **Multiple Methods**: Z-Score, Median Absolute Deviation, and custom algorithms
- **Adaptive Learning**: Models adapt as new data arrives

### Risk Assessment
- **Real-Time Risk Scoring**: 0-100 risk score with severity levels (Low/Medium/High/Critical)
- **Multi-Event Analysis**: Combined risk assessment when multiple events occur simultaneously
- **Location-Aware**: Risk multipliers based on geographic characteristics

### AI Response Planning
- **Automatic Action Plans**: AI generates recommended actions based on event type and severity
- **Resource Estimation**: Calculates required resources (personnel, equipment, vehicles, etc.)
- **Impact Forecasting**: Estimates affected population and potential damage costs
- **Priority Optimization**: Prioritizes actions based on severity and urgency

### Real-Time Dashboard
- **Live Map**: Interactive map showing event locations and severity
- **Risk Gauge**: Visual representation of current risk score
- **Event Tracking**: Real-time event list with filtering and sorting
- **Alert Management**: Critical alerts with send status tracking
- **Response Plans**: Comprehensive disaster response planning interface
- **WebSocket Updates**: Live data streaming to all connected clients

### Production Ready
- **PostgreSQL Database**: Persistent event and alert storage
- **Redis Caching**: High-performance real-time data processing
- **Docker Containerization**: Easy deployment across environments
- **CI/CD Pipeline**: Automated testing and deployment
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **Comprehensive Logging**: Structured logging with audit trails

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard (Frontend)               │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Live Map    │ │  Metrics     │ │  Alerts      │       │
│  │              │ │              │ │              │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          │                                  │
│                   WebSocket Connection                      │
└─────────────────────────────────────────────────────────────┘
                           │
                    /api endpoint
                           │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  REST API & WebSocket Server                       │   │
│  │  - Events Management                               │   │
│  │  - Alerts & Notifications                          │   │
│  │  - Response Plans                                  │   │
│  │  - Data Feeds Management                           │   │
│  └────────────────────────────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────┬──────────────┬──────────────┐           │
│  │              │              │              │           │
│  ▼              ▼              ▼              ▼           │
│ ┌────────────┐┌────────────┐┌────────────┐┌──────────┐  │
│ │ Data Stream││ Anomaly    ││ Risk       ││ AI       │  │
│ │ Processor  ││ Detection  ││ Assessment ││ Planner  │  │
│ │            ││            ││            ││          │  │
│ │ Real-time  ││ Isolation  ││ Severity   ││ Response │  │
│ │ API Client ││ Forest +   ││ Scoring    ││ Plans    │  │
│ │            ││ Z-Score    ││            ││          │  │
│ └────────────┘└────────────┘└────────────┘└──────────┘  │
│                         │                                   │
└─────────────────────────┼────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐      ┌──────────┐      ┌──────────┐
    │PostgreSQL     │  Redis   │      │ Real-time│
    │ Database      │  Cache   │      │  APIs    │
    │              │          │      │          │
    │ Events        │ Streams  │      │• Weather │
    │ Alerts        │ Sessions │      │• USGS EQ │
    │ Plans         │          │      │• Other   │
    └────────┘      └──────────┘      └──────────┘
```

---

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **ML/Analytics**: Scikit-learn, NumPy, Pandas, SciPy
- **Async**: asyncio, aiohttp
- **ORM**: SQLAlchemy 2.0+
- **Logging**: structlog, python-json-logger
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript 5+
- **Build Tool**: Vite 5+
- **Styling**: Tailwind CSS 3+
- **Mapping**: Leaflet + React-Leaflet
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Testing**: Vitest

### DevOps & Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Web Server**: Nginx
- **Reverse Proxy**: Nginx
- **Container Registry**: GitHub Container Registry (GHCR)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)
- PostgreSQL client tools (optional, for manual DB access)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/bharat-resilience-ai.git
cd bharat-resilience-ai

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Initialize database (if needed)
docker-compose exec backend python -c "from backend.database import init_db; asyncio.run(init_db())"

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Access the application:**
- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000/api
- **API Documentation**: http://localhost:8000/api/docs
- **pgAdmin**: http://localhost:5050
- **Redis Commander**: http://localhost:8081

### Local Development

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local settings

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
(Optional - can be implemented with JWT tokens)

### Endpoints

#### Events
- `GET /events` - List all events
- `GET /events/{id}` - Get specific event
- `POST /events` - Create event
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event
- `GET /events/stats/summary` - Event statistics

#### Alerts
- `GET /alerts` - List all alerts
- `GET /alerts/{id}` - Get specific alert
- `POST /alerts` - Create alert
- `PUT /alerts/{id}/send` - Send alert
- `GET /alerts/stats/critical` - Critical alerts statistics

#### Response Plans
- `GET /response-plans` - List all plans
- `GET /response-plans/{id}` - Get specific plan
- `POST /response-plans` - Create plan
- `PUT /response-plans/{id}/status` - Update plan status
- `GET /response-plans/event/{event_id}` - Get plan for event

#### Data Feeds
- `GET /data-feeds` - List all feeds
- `GET /data-feeds/{id}` - Get specific feed
- `POST /data-feeds` - Create feed
- `PUT /data-feeds/{id}` - Update feed
- `GET /data-feeds/{id}/data` - Get feed data points
- `POST /data-feeds/{id}/data` - Add data point
- `GET /data-feeds/stats/feed-health` - Feed health status

#### WebSocket
- `WS /ws/events` - Real-time event streaming

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Application
APP_NAME=BharatResilience AI
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/bharat_resilience
SQLALCHEMY_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=yourpassword
CACHE_TTL=300

# JWT (if authentication is enabled)
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
WEATHER_API_KEY=optional_api_key
WEATHER_API_PROVIDER=open-meteo
EARTHQUAKE_API_URL=https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson

# Alerts
ALERT_THRESHOLD=70
EMAIL_FROM=alerts@bharatresilience.ai

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## 📊 Data Models

### Event
- ID, Type, Location, Coordinates
- Severity (0-100), Confidence (0-1)
- Description, Data Source
- Raw sensor data (JSON)
- Timestamps

### Alert
- ID, Event ID
- Severity, Title, Message
- Recipient emails
- Sent status and timestamp

### Response Plan
- ID, Event ID
- Title, Description
- Recommended actions (JSON)
- Resource requirements (JSON)
- Status (draft/approved/executing/completed)
- Priority level (1-100)
- Impact estimates

### Data Feed
- ID, Name, Source
- API URL, Type
- Polling interval
- Last polled timestamp
- Error count

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_anomaly_detection.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm run test

# Run with coverage
npm run test -- --coverage
```

---

## 🐳 Docker Deployment

### Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Production Deployment

```bash
# Use production compose file (if available)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Execute commands in container
docker-compose exec backend python -c "..."

# Scale services
docker-compose up -d --scale backend=3
```

---

## 📈 Monitoring & Logging

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost/
```

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical messages requiring immediate attention

### Log Files
- Backend: `docker-compose logs backend`
- Frontend: `docker-compose logs frontend`
- Database: `docker-compose logs postgres`

---

## 🔒 Security

### Best Practices Implemented
- ✅ Secrets management via environment variables
- ✅ Non-root container users
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS protection
- ✅ Health checks with container restart
- ✅ Input validation (Pydantic schemas)
- ✅ Rate limiting support
- ✅ HTTPS ready (configure in nginx.conf)

### Security Checklist
- [ ] Change default passwords in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Enable HTTPS in production
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Database backups
- [ ] API key rotation

---

## 📝 Development Workflow

### Adding a New Feature

1. **Create a branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes**
   - Update backend code in `backend/`
   - Update frontend code in `frontend/src/`
   - Write tests

3. **Test locally**
   ```bash
   docker-compose up -d
   # Test your changes
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

5. **Create Pull Request**
   - CI/CD pipeline runs automatically
   - Code review required
   - Merge to main/develop

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support & Contact

- **Documentation**: Check the `/docs` folder
- **Issues**: GitHub Issues
- **Email**: support@bharatresilience.ai
- **Discord**: [Community Server]

---

## 🙏 Acknowledgments

- Open-Meteo for free weather API
- USGS for earthquake data
- OpenStreetMap for mapping data
- FastAPI and React communities

---

## 📊 Project Status

- **Current Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: 2024
- **Maintainers**: BharatResilience Team

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Docker Documentation](https://docs.docker.com/)

---

**Made with ❤️ for disaster resilience and community safety.**
