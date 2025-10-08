.PHONY: help setup install dev build test lint format clean docker-up docker-down deploy-dev deploy-staging deploy-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - install all dependencies
	@echo "🚀 Setting up OMK Hive..."
	@./scripts/setup/init.sh

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	@npm install
	@cd contracts/ethereum && npm install
	@cd backend/api-gateway && npm install
	@cd backend/queen-ai && pip install -r requirements.txt
	@cd frontend/web && npm install

dev: ## Start development environment
	@echo "🔥 Starting development environment..."
	@docker-compose -f docker-compose.dev.yml up

dev-services: ## Start only support services (DB, Redis, etc.)
	@docker-compose -f docker-compose.dev.yml up postgres redis kafka

build: ## Build all services
	@echo "🏗️  Building all services..."
	@npm run build

build-contracts: ## Build smart contracts
	@cd contracts/ethereum && npm run compile

build-backend: ## Build backend services
	@cd backend/api-gateway && npm run build

build-frontend: ## Build frontend
	@cd frontend/web && npm run build

test: ## Run all tests
	@echo "🧪 Running all tests..."
	@npm run test

test-contracts: ## Test smart contracts
	@cd contracts/ethereum && npm run test

test-backend: ## Test backend
	@cd backend/api-gateway && npm run test

test-frontend: ## Test frontend
	@cd frontend/web && npm run test

test-queen: ## Test Queen AI
	@cd backend/queen-ai && pytest

lint: ## Lint all code
	@echo "🔍 Linting code..."
	@npm run lint

format: ## Format all code
	@echo "✨ Formatting code..."
	@npm run format

format-check: ## Check code formatting
	@npm run format:check

clean: ## Clean all build artifacts and dependencies
	@echo "🧹 Cleaning..."
	@npm run clean
	@rm -rf contracts/ethereum/artifacts
	@rm -rf contracts/ethereum/cache
	@rm -rf backend/api-gateway/dist
	@rm -rf frontend/web/.next

docker-build: ## Build Docker images
	@docker-compose build

docker-up: ## Start Docker containers
	@docker-compose up -d

docker-down: ## Stop Docker containers
	@docker-compose down

docker-logs: ## View Docker logs
	@docker-compose logs -f

deploy-dev: ## Deploy to development
	@echo "🚀 Deploying to development..."
	@./scripts/deploy/dev.sh

deploy-staging: ## Deploy to staging
	@echo "🚀 Deploying to staging..."
	@./scripts/deploy/staging.sh

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	@./scripts/deploy/production.sh

db-migrate: ## Run database migrations
	@./scripts/database/migrate.sh

db-seed: ## Seed database
	@./scripts/database/seed.sh

logs: ## View logs
	@tail -f logs/*.log

verify-contracts: ## Verify contracts on Etherscan
	@cd contracts/ethereum && npm run verify

security-scan: ## Run security scans
	@cd contracts/ethereum && npm run security

coverage: ## Generate test coverage report
	@npm run test:coverage
