# Makefile for common tasks

.PHONY: help up down build migrate test clean logs shell

help:
	@echo "Multi-Tenant SaaS Platform - Make Commands"
	@echo ""
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build Docker images"
	@echo "  make migrate     - Run database migrations"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Open shell in API container"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose exec api alembic upgrade head

test:
	docker-compose exec api pytest

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

logs:
	docker-compose logs -f

shell:
	docker-compose exec api /bin/bash
