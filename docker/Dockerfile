FROM python:3.13-slim

# Build arguments for different modes
ARG BUILD_MODE=development
ARG ENABLE_HEALTHCHECK=false

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY src/ .

# Copy translation validation script
COPY docker/check_translations.sh /tmp/check_translations.sh
RUN chmod +x /tmp/check_translations.sh

# Validate and compile translations
RUN /tmp/check_translations.sh && rm /tmp/check_translations.sh

# Collect static files
RUN if [ "$BUILD_MODE" = "production" ]; then \
        echo "=== Production build: collecting static files ===" && \
        python manage.py collectstatic --noinput --clear; \
    else \
        echo "=== Development build: skipping static files ===" && \
        python manage.py collectstatic --noinput --clear || true; \
    fi

# Install gosu for user switching in production
RUN if [ "$BUILD_MODE" = "production" ]; then \
        echo "=== Installing gosu for production user switching ===" && \
        apt-get update && \
        apt-get install -y gosu && \
        rm -rf /var/lib/apt/lists/* && \
        adduser --disabled-password --gecos '' appuser; \
    else \
        echo "=== Development build: skipping gosu installation ==="; \
    fi

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Add health check for production
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD if [ "$ENABLE_HEALTHCHECK" = "true" ]; then \
            python -c "import requests; requests.get('http://localhost:8000/panel/login/', timeout=10)" || exit 1; \
        else \
            exit 0; \
        fi

# Set entrypoint and default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]