# ⚽ Footy-Brain v5

> **Real-time football data ingestion and analysis platform with live betting odds**

A production-ready microservices platform that ingests live football data from API-Football, processes it in real-time using TimescaleDB, and provides a modern web dashboard for monitoring matches, odds, and statistics.

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.11+ and **Poetry**
- **Docker** and **Docker Compose**
- **RapidAPI Key** for [API-Football](https://rapidapi.com/api-sports/api/api-football)

### 1. Clone & Setup

```bash
git clone https://github.com/footy-brain/footy-brain.git
cd footy-brain

# Copy environment file and configure
cp .env.example .env
# Edit .env and add your RAPIDAPI_KEY

# Install dependencies
pnpm install
poetry install
```

### 2. Start with Docker (Recommended)

```bash
# Start all services
docker compose up -d

# Check service health
docker compose ps

# View logs
docker compose logs -f

# Access the dashboard
open http://localhost:3000
```

### 3. Development Mode (Without Docker)

```bash
# Start database services only
docker compose up -d pg redis

# Start API server
cd apps/api-server
poetry run uvicorn main:app --reload --port 8000

# Start web dashboard (in another terminal)
cd apps/web-dashboard
pnpm dev

# Access the dashboard
open http://localhost:3000
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │   API Server    │    │  Live Worker    │
│   (Next.js 14)  │◄──►│   (FastAPI)     │◄──►│  (Real-time)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  TimescaleDB    │    │     Redis       │
                       │  (PostgreSQL)   │    │   (Cache/Pub)   │
                       └─────────────────┘    └─────────────────┘
```

### Core Components

- **🎛️ API Server**: FastAPI-based REST API with WebSocket support
- **💻 Web Dashboard**: Next.js 14 dashboard with real-time updates
- **⚡ Live Worker**: Real-time data ingestion (5-10s cycles)
- **🕑 Frame Worker**: 1-minute summary aggregation
- **🗄️ TimescaleDB**: Time-series database for efficient data storage
- **🔄 Redis**: Caching and real-time pub/sub messaging
- **📊 Celery**: Background task processing

## 📁 Project Structure

```
footy-brain/
├── apps/
│   ├── api-server/          # FastAPI backend
│   ├── web-dashboard/       # Next.js frontend
│   ├── live-worker/         # Real-time data ingestion
│   └── frame-worker/        # Data aggregation
├── config/                  # YAML configurations
├── database/                # SQL schemas and seeds
├── tools/                   # API-Football wrappers
├── infra/                   # K8s, Helm, CI/CD
└── tests/                   # Test suites
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Required
RAPIDAPI_KEY=your_rapidapi_key_here
JWT_SECRET=your_jwt_secret
NEXTAUTH_SECRET=your_nextauth_secret

# Database
DATABASE_URL=postgresql://footy:password@localhost:5432/footy
REDIS_URL=redis://localhost:6379/0

# Features
FEATURE_LIVE_ODDS=true
FEATURE_LIVE_EVENTS=true
WEBSOCKET_ENABLED=true
```

### YAML Configurations

- **`config/app.yml`**: Core application settings
- **`config/leagues.yml`**: Leagues and competitions to track
- **`config/workers.yml`**: Background job schedules

## 🎯 Features

### ✅ Implemented

- **Real-time Data Ingestion**: Live odds, events, and statistics
- **WebSocket Support**: Real-time updates to web dashboard
- **Time-series Storage**: Efficient data storage with TimescaleDB
- **Microservices Architecture**: Scalable and maintainable
- **Modern Web Dashboard**: Built with Next.js 14 and shadcn/ui
- **Background Processing**: Celery-based task queue
- **API Wrappers**: Complete API-Football integration
- **Docker Support**: Full containerization
- **Type Safety**: TypeScript frontend, Python type hints

### 🚧 Roadmap

- **Machine Learning**: Predictive models for match outcomes
- **Advanced Analytics**: Statistical analysis and insights
- **Mobile App**: React Native mobile application
- **Kubernetes**: Production-ready K8s deployment
- **Monitoring**: Grafana dashboards and alerting

## 🧪 Testing

```bash
# Python tests
poetry run pytest

# JavaScript tests
pnpm test

# Integration tests
pnpm test:integration

# Linting and formatting
pnpm lint
poetry run ruff check
poetry run mypy .
```

## 📊 API Endpoints

### Core Endpoints

- **`GET /fixtures`**: Match fixtures with filtering
- **`GET /live/{fixture_id}`**: Live match data
- **`GET /odds/live/{fixture_id}`**: Real-time odds
- **`WS /ws/live/{fixture_id}`**: WebSocket for live updates

### Management Endpoints

- **`GET /plugins`**: Available API wrappers
- **`GET /settings/leagues`**: League configurations
- **`POST /cronjobs`**: Background job management

## 🚀 Deployment

### Docker Compose (Development)

```bash
docker compose up -d
```

### Kubernetes (Production)

```bash
helm install footy-brain ./infra/helm/footy-brain \
  --set image.tag=latest \
  --set rapidapi.key=$RAPIDAPI_KEY
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation
- Ensure all checks pass: `pnpm lint && pnpm test`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [API-Football](https://www.api-football.com/) for providing comprehensive football data
- [TimescaleDB](https://www.timescale.com/) for time-series database capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python web framework
- [Next.js](https://nextjs.org/) for the React framework
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components

## 📞 Support

- **Documentation**: [docs.footy-brain.com](https://docs.footy-brain.com)
- **Issues**: [GitHub Issues](https://github.com/footy-brain/footy-brain/issues)
- **Discussions**: [GitHub Discussions](https://github.com/footy-brain/footy-brain/discussions)

---

**Made with ⚽ by the Footy-Brain Team**
