#!/bin/bash

# WHMCS Admin Panel - Docker Entrypoint Script
# Handles different modes: development vs production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[ENTRYPOINT]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ENTRYPOINT]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ENTRYPOINT]${NC} $1"
}

print_error() {
    echo -e "${RED}[ENTRYPOINT]${NC} $1"
}

# Determine mode
BUILD_MODE=${BUILD_MODE:-development}
DEBUG=${DEBUG:-1}

print_info "Starting WHMCS Admin Panel in $BUILD_MODE mode"

# Production-specific setup
if [ "$BUILD_MODE" = "production" ]; then
    print_info "Production mode detected"
    
    # Switch to non-root user if running as root
    if [ "$(id -u)" = "0" ]; then
        print_info "Switching to appuser for security"
        # Change ownership of files to appuser
        chown -R appuser:appuser /app
        # Execute command as appuser
        exec gosu appuser "$@"
    fi
    
    # Ensure static files are collected
    if [ ! -d "/app/staticfiles" ] || [ -z "$(ls -A /app/staticfiles)" ]; then
        print_info "Collecting static files for production"
        python manage.py collectstatic --noinput --clear
    fi
    
else
    print_info "Development mode detected"
fi

# Database migrations (both dev and prod)
print_info "Checking database migrations"
python manage.py migrate --check || {
    print_warning "Migrations needed, applying..."
    python manage.py migrate
}

# Create admin user if needed (development only)
if [ "$BUILD_MODE" = "development" ] && [ "$DEBUG" = "1" ]; then
    print_info "Creating admin user for development"
    python manage.py create_admin || print_warning "Admin user creation failed or already exists"
fi

# Compile translations if .po files are newer than .mo files
print_info "Checking translation files"
if find locale -name "*.po" -newer locale -name "*.mo" 2>/dev/null | grep -q .; then
    print_info "Recompiling translations"
    python manage.py compilemessages
fi

print_success "Initialization complete, starting application"

# Execute the main command
exec "$@"