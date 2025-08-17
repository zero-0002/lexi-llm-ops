# Legal Retrieval System - Docker Management Makefile
# =======================================================
# Quick commands for building, pushing and managing Docker services
# =======================================================

# Default values
REGISTRY ?= docker.io
TAG ?= latest
TARGET ?= all

# Docker Compose settings
COMPOSE_FILE ?= docker-compose.yml
PROJECT_NAME ?= legal-retrieval

# Colors for output (cross-shell compatible)
BLUE = \e[34m
GREEN = \e[32m
YELLOW = \e[33m
RED = \e[31m
NC = \e[0m

# Help target (default)
.PHONY: help
help:
	@echo -e "$(BLUE)[Legal Retrieval System - Docker Management]$(NC)"
	@echo -e "=================================================="
	@echo -e ""
	@echo -e "$(GREEN)[Build Commands]$(NC)"
	@echo -e "  make build                    Build all services"
	@echo -e "  make build-backend           Build backend service only"
	@echo -e "  make build-frontend          Build frontend service only"
	@echo -e "  make build-clean             Build without Docker cache"
	@echo -e ""
	@echo -e "$(GREEN)[Deploy Commands]$(NC)"
	@echo -e "  make up                      Start all services"
	@echo -e "  make down                    Stop all services"
	@echo -e "  make restart                 Restart all services"
	@echo -e "  make logs                    View all service logs"
	@echo -e "  make status                  Show service status"
	@echo -e ""
	@echo -e "$(GREEN)[Development Commands]$(NC)"
	@echo -e "  make dev-up                  Start development with build"
	@echo -e "  make dev-down                Stop and remove volumes"
	@echo -e "  make dev-logs                Follow development logs"
	@echo -e "  make dev-shell               Access backend container shell"
	@echo -e ""
	@echo -e "$(GREEN)[Service Commands]$(NC)"
	@echo -e "  make backend-logs            View backend API logs"
	@echo -e "  make worker-logs             View worker logs"
	@echo -e "  make db-logs                 View database logs"
	@echo -e ""
	@echo -e "$(GREEN)[Testing Commands]$(NC)"
	@echo -e "  make test                    Run all tests"
	@echo -e "  make test-smoke              Run smoke tests only"
	@echo -e "  make test-api                Run API tests only"
	@echo -e "  make test-health             Check service health"
	@echo -e ""
	@echo -e "$(GREEN)[Cleanup Commands]$(NC)"
	@echo -e "  make clean                   Clean Docker resources"
	@echo -e "  make clean-volumes           Remove all volumes (DATA LOSS!)"
	@echo -e "  make clean-all               Deep clean everything"
	@echo -e ""
	@echo -e "$(GREEN)[Utility Commands]$(NC)"
	@echo -e "  make health                  Check service health"
	@echo -e "  make show-urls               Show service URLs"
	@echo -e "  make check-env               Check environment"
	@echo -e ""
	@echo -e "$(YELLOW)[Examples]$(NC)"
	@echo -e "  make build-backend TAG=v1.0.0"
	@echo -e "  make up"
	@echo -e "  make health"

# =======================================================
# DOCKER COMPOSE TARGETS
# =======================================================

.PHONY: up down restart logs status
up:
	@echo "$(BLUE)🚀 Starting all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ All services started$(NC)"
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Flower: http://localhost:5555"
	@echo "Qdrant: http://localhost:6333"

down:
	@echo "$(BLUE)🛑 Stopping all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ All services stopped$(NC)"

restart:
	@echo "$(BLUE)🔄 Restarting all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

logs:
	@echo "$(BLUE)📋 Viewing all service logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f

status:
	@echo "$(BLUE)📊 Service status:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

# =======================================================
# DEVELOPMENT TARGETS
# =======================================================

.PHONY: dev-up dev-down dev-logs dev-shell
dev-up:
	@echo "$(BLUE)🚀 Starting development environment...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) up --build -d
	@echo "$(GREEN)✅ Development environment started$(NC)"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Flower: http://localhost:5555"

dev-down:
	@echo "$(BLUE)🛑 Stopping development environment...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(GREEN)✅ Development environment stopped$(NC)"

dev-logs:
	@echo "$(BLUE)📋 Following development logs...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f backend-api celery-worker-rag frontend

dev-shell:
	@echo "$(BLUE)💻 Accessing backend container shell...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec backend-api bash

# =======================================================
# SERVICE-SPECIFIC LOG TARGETS
# =======================================================

.PHONY: backend-logs worker-logs db-logs
backend-logs:
	@echo "$(BLUE)📋 Backend API logs:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f backend-api

worker-logs:
	@echo "$(BLUE)⚙️ Celery worker logs:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f celery-worker-rag celery-worker-embed celery-worker-retrieval celery-worker-link

db-logs:
	@echo "$(BLUE)📋 Database logs:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) logs -f mongodb redis qdrant

# =======================================================
# BUILD TARGETS
# =======================================================

.PHONY: build build-backend build-frontend build-clean
build:
	@echo "$(BLUE)🔨 Building all services...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✅ All services built$(NC)"

build-backend:
	@echo "$(BLUE)🔨 Building backend service...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build backend-api
	@echo "$(GREEN)✅ Backend built$(NC)"

build-frontend:
	@echo "$(BLUE)🔨 Building frontend service...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build frontend
	@echo "$(GREEN)✅ Frontend built$(NC)"

build-clean:
	@echo "$(BLUE)🔨 Building all services (no cache)...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "$(GREEN)✅ All services built (clean)$(NC)"

# =======================================================
# CLEANUP TARGETS
# =======================================================

.PHONY: clean clean-volumes clean-all
clean:
	@echo "$(YELLOW)🧹 Cleaning unused Docker resources...$(NC)"
	@docker system prune -f
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

clean-volumes:
	@echo "$(RED)⚠️  WARNING: This will remove ALL project volumes!$(NC)"
	@echo "This will delete all MongoDB, Redis, and Qdrant data permanently."
	@echo "Type 'DELETE' to confirm:"
	@read confirm && [ "$$confirm" = "DELETE" ] || exit 1
	@docker-compose -f $(COMPOSE_FILE) down -v
	@docker volume prune -f
	@echo "$(GREEN)✅ All volumes removed$(NC)"

clean-all:
	@echo "$(RED)⚠️  WARNING: This will remove ALL Docker resources!$(NC)"
	@echo "Type 'CONFIRM' to proceed:"
	@read confirm && [ "$$confirm" = "CONFIRM" ] || exit 1
	@docker-compose -f $(COMPOSE_FILE) down -v
	@docker system prune -a -f --volumes
	@echo "$(GREEN)✅ Complete cleanup finished$(NC)"

# =======================================================
# TESTING TARGETS
# =======================================================

.PHONY: test test-smoke test-api test-health
test:
	@echo "$(BLUE)🧪 Running comprehensive test suite...$(NC)"
	@if [ -f ./tests/run_docker_tests.sh ]; then \
		./tests/run_docker_tests.sh --command full; \
	else \
		echo "$(RED)❌ Test script not found$(NC)"; \
		exit 1; \
	fi

test-smoke:
	@echo "$(BLUE)🧪 Running smoke tests...$(NC)"
	@if [ -f ./tests/run_docker_tests.sh ]; then \
		./tests/run_docker_tests.sh --command test --test-type smoke; \
	else \
		echo "$(YELLOW)⚠️ Using basic health check instead$(NC)"; \
		make health; \
	fi

test-api:
	@echo "$(BLUE)🧪 Running API tests...$(NC)"
	@if [ -f ./tests/api/comprehensive_backend_test.py ]; then \
		python3 ./tests/api/comprehensive_backend_test.py; \
	else \
		echo "$(YELLOW)⚠️ API test script not found, using health check$(NC)"; \
		make health; \
	fi

test-health:
	@echo "$(BLUE)🧪 Quick health check...$(NC)"
	@make health

# =======================================================
# UTILITY TARGETS
# =======================================================

.PHONY: health check-env show-urls
health:
	@echo "$(BLUE)🩺 Service Health Check$(NC)"
	@echo "==========================="
	@echo ""
	@echo "$(GREEN)Backend API:$(NC)"
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo ""
	@echo "$(GREEN)Frontend:$(NC)"
	@curl -f http://localhost:3000 2>/dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo ""
	@echo "$(GREEN)Celery Flower:$(NC)"
	@curl -f http://localhost:5555 2>/dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"
	@echo ""
	@echo "$(GREEN)Qdrant:$(NC)"
	@curl -f http://localhost:6333/ 2>/dev/null >/dev/null && echo "✅ Healthy" || echo "❌ Unhealthy"

check-env:
	@echo "$(BLUE)🔍 Environment Check$(NC)"
	@echo "====================="
	@echo "Registry: $(REGISTRY)"
	@echo "Tag: $(TAG)"
	@echo "Compose File: $(COMPOSE_FILE)"
	@echo "Project Name: $(PROJECT_NAME)"
	@echo ""
	@echo "$(BLUE)📋 Required Files:$(NC)"
	@if [ -f .env ]; then \
		echo "✅ .env file found"; \
	else \
		echo "❌ .env file not found - copy from .env.example"; \
	fi
	@if [ -f $(COMPOSE_FILE) ]; then \
		echo "✅ $(COMPOSE_FILE) found"; \
	else \
		echo "❌ $(COMPOSE_FILE) not found"; \
	fi
	@echo ""
	@echo "$(BLUE)🔧 Required Tools:$(NC)"
	@command -v docker >/dev/null 2>&1 && echo "✅ Docker installed" || echo "❌ Docker not found"
	@command -v docker-compose >/dev/null 2>&1 && echo "✅ Docker Compose installed" || echo "❌ Docker Compose not found"

show-urls:
	@echo "$(BLUE)🌐 Service URLs$(NC)"
	@echo "================"
	@echo "Frontend:       http://localhost:3000"
	@echo "Backend API:    http://localhost:8000"
	@echo "API Docs:       http://localhost:8000/docs"
	@echo "Celery Flower:  http://localhost:5555"
	@echo "Qdrant UI:      http://localhost:6333/dashboard"
	@echo "MongoDB:        mongodb://localhost:27017"
	@echo "Redis:          redis://localhost:6379"

# =======================================================
# QUICK START HELPERS
# =======================================================

.PHONY: quick-start stop-all
quick-start:
	@echo "$(BLUE)🚀 Quick Start - Legal Retrieval System$(NC)"
	@echo "=========================================="
	@echo ""
	@echo "$(YELLOW)1. Checking environment...$(NC)"
	@make --no-print-directory check-env
	@echo ""
	@echo "$(YELLOW)2. Starting all services...$(NC)"
	@make --no-print-directory dev-up
	@echo ""
	@echo "$(YELLOW)3. Waiting for services to be ready...$(NC)"
	@sleep 10
	@echo ""
	@echo "$(YELLOW)4. Health check...$(NC)"
	@make --no-print-directory health
	@echo ""
	@make --no-print-directory show-urls

stop-all:
	@echo "$(BLUE)🛑 Stopping All Services$(NC)"
	@echo "============================"
	@make --no-print-directory down
	@echo "$(GREEN)✅ All services stopped$(NC)"
