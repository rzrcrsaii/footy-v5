# Footy-Brain v5 Makefile
# Development and deployment automation

.PHONY: help install dev build test lint format clean docker-build docker-up docker-down

# Default target
help:
	@echo "Footy-Brain v5 Development Commands"
	@echo "=================================="
	@echo "install     - Install all dependencies"
	@echo "dev         - Start development environment"
	@echo "build       - Build all services"
	@echo "test        - Run all tests"
	@echo "lint        - Run linting checks"
	@echo "format      - Format code"
	@echo "clean       - Clean build artifacts"
	@echo "docker-build - Build Docker images"
	@echo "docker-up   - Start Docker services"
	@echo "docker-down - Stop Docker services"

# Installation
install:
	@echo "Installing Python dependencies..."
	poetry install
	@echo "Installing Node.js dependencies..."
	cd apps/web-dashboard && pnpm install
	@echo "Dependencies installed successfully!"

# Development
dev:
	@echo "Starting development environment..."
	docker-compose up -d pg redis
	@echo "Database and Redis started. Run 'make dev-api' and 'make dev-web' in separate terminals."

dev-api:
	@echo "Starting API server in development mode..."
	cd apps/api-server && python main.py

dev-web:
	@echo "Starting web dashboard in development mode..."
	cd apps/web-dashboard && pnpm dev

dev-workers:
	@echo "Starting workers in development mode..."
	python apps/live-worker/main.py &
	python apps/frame-worker/main.py &

# Building
build:
	@echo "Building all services..."
	docker-compose build

build-api:
	@echo "Building API server..."
	docker build -f apps/api-server/Dockerfile -t footy-brain-api .

build-web:
	@echo "Building web dashboard..."
	docker build -f apps/web-dashboard/Dockerfile -t footy-brain-web .

# Testing
test:
	@echo "Running all tests..."
	pytest

test-unit:
	@echo "Running unit tests..."
	pytest -m unit

test-integration:
	@echo "Running integration tests..."
	pytest -m integration

test-api:
	@echo "Running API tests..."
	pytest tests/api_server/

test-tools:
	@echo "Running tools tests..."
	pytest tests/tools/

test-coverage:
	@echo "Running tests with coverage..."
	pytest --cov=tools --cov=apps --cov-report=html

# Code Quality
lint:
	@echo "Running linting checks..."
	ruff check .
	mypy --strict tools/ apps/
	cd apps/web-dashboard && pnpm lint

lint-fix:
	@echo "Fixing linting issues..."
	ruff check --fix .
	cd apps/web-dashboard && pnpm lint:fix

format:
	@echo "Formatting code..."
	ruff format .
	cd apps/web-dashboard && pnpm format

type-check:
	@echo "Running type checks..."
	mypy --strict tools/ apps/
	cd apps/web-dashboard && pnpm type-check

# Database
db-init:
	@echo "Initializing database..."
	python apps/api-server/db/init.py

db-reset:
	@echo "Resetting database..."
	python apps/api-server/db/init.py --reset

db-migrate:
	@echo "Running database migrations..."
	python apps/api-server/db/init.py --force

# Docker Operations
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

docker-restart:
	@echo "Restarting Docker services..."
	docker-compose restart

# Production
prod-build:
	@echo "Building for production..."
	docker-compose -f docker-compose.yml build

prod-up:
	@echo "Starting production services..."
	docker-compose -f docker-compose.yml up -d

prod-down:
	@echo "Stopping production services..."
	docker-compose -f docker-compose.yml down

# Monitoring
monitor-up:
	@echo "Starting monitoring services..."
	docker-compose --profile monitoring up -d

monitor-down:
	@echo "Stopping monitoring services..."
	docker-compose --profile monitoring down

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	cd apps/web-dashboard && rm -rf .next out dist

clean-docker:
	@echo "Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# Health Checks
health:
	@echo "Checking service health..."
	curl -f http://localhost:8000/health || echo "API server not responding"
	curl -f http://localhost:3000/api/health || echo "Web dashboard not responding"

# Logs
logs-api:
	@echo "Showing API server logs..."
	docker-compose logs -f api

logs-web:
	@echo "Showing web dashboard logs..."
	docker-compose logs -f web

logs-workers:
	@echo "Showing worker logs..."
	docker-compose logs -f live-worker frame-worker

logs-db:
	@echo "Showing database logs..."
	docker-compose logs -f pg

# Security
security-check:
	@echo "Running security checks..."
	safety check
	cd apps/web-dashboard && pnpm audit

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation generation not implemented yet"

# Quick start for new developers
quickstart:
	@echo "Quick start for new developers..."
	@echo "1. Installing dependencies..."
	make install
	@echo "2. Starting infrastructure..."
	docker-compose up -d pg redis
	@echo "3. Initializing database..."
	make db-init
	@echo "4. Running tests..."
	make test
	@echo "Quick start completed! Run 'make dev-api' and 'make dev-web' to start development."
