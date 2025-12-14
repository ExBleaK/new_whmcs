# WHMCS Admin Panel - Makefile

.PHONY: help dev prod build test translations clean

# Default target
help:
	@echo "WHMCS Admin Panel - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development environment"
	@echo "  make dev-build        - Build and start development environment"
	@echo "  make logs             - Show development logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod             - Start production environment"
	@echo "  make prod-build       - Build and start production environment"
	@echo ""
	@echo "Translations:"
	@echo "  make translations     - Update and compile translations"
	@echo "  make translations-uk  - Update Ukrainian translations only"
	@echo "  make translations-test - Test translation quality"
	@echo "  make translations-stats - Show translation statistics"
	@echo "  make fix-english      - Fix English translations (msgstr = msgid)"
	@echo "  make add-lang LANG=de NAME=Deutsch - Add new language"
	@echo ""
	@echo "Testing & Maintenance:"
	@echo "  make test             - Run tests"
	@echo "  make clean            - Clean up containers and volumes"
	@echo "  make shell            - Open shell in web container"
	@echo ""

# Development environment
dev:
	docker-compose -f docker/docker-compose.yml up

dev-build:
	docker-compose -f docker/docker-compose.yml up --build

logs:
	docker-compose -f docker/docker-compose.yml logs -f web

# Production environment
prod:
	docker-compose -f docker/docker-compose.yml --profile production up web-prod

prod-build:
	docker-compose -f docker/docker-compose.yml --profile production up --build web-prod

# Translation management
translations:
	@echo "Updating all translations..."
	python dev_tools/translations.py update

translations-uk:
	@echo "Updating Ukrainian translations..."
	python dev_tools/translations.py update uk

translations-test:
	@echo "Testing translation quality..."
	python dev_tools/translations.py test

translations-stats:
	@echo "Showing translation statistics..."
	python dev_tools/translations.py stats

fix-english:
	@echo "Fixing English translations..."
	python dev_tools/translations.py fix-english

add-lang:
	@if [ -z "$(LANG)" ] || [ -z "$(NAME)" ]; then \
		echo "Usage: make add-lang LANG=de NAME=Deutsch"; \
		exit 1; \
	fi
	@echo "Adding language: $(NAME) ($(LANG))"
	python dev_tools/translations.py add $(LANG) "$(NAME)"

# Testing
test:
	@echo "Running tests..."
	docker-compose -f docker/docker-compose.yml exec web python manage.py test

# Maintenance
clean:
	@echo "Cleaning up Docker containers and volumes..."
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f

shell:
	docker-compose -f docker/docker-compose.yml exec web /bin/bash

# Build only (without starting)
build:
	@echo "Building development image..."
	docker-compose -f docker/docker-compose.yml build web

build-prod:
	@echo "Building production image..."
	docker-compose -f docker/docker-compose.yml --profile production build web-prod

# Direct Docker builds
build-dev-direct:
	@echo "Building development image directly..."
	docker build -f docker/Dockerfile --build-arg BUILD_MODE=development -t whmcs-admin:dev .

build-prod-direct:
	@echo "Building production image directly..."
	docker build -f docker/Dockerfile --build-arg BUILD_MODE=production --build-arg ENABLE_HEALTHCHECK=true -t whmcs-admin:prod .

# Database operations
migrate:
	docker-compose -f docker/docker-compose.yml exec web python manage.py migrate

create-admin:
	docker-compose -f docker/docker-compose.yml exec web python manage.py create_admin

# Show container status
status:
	docker-compose -f docker/docker-compose.yml ps