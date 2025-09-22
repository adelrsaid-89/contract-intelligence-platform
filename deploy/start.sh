#!/bin/bash
set -e

# Enova Contract Intelligence Platform - Startup Script
echo "🚀 Starting Enova Contract Intelligence Platform..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please review and update the .env file with your settings before running again."
    echo "💡 Tip: Set your Azure/OpenAI keys in .env to enable cloud AI features."
    exit 1
fi

# Load environment variables
source .env

# Determine compose files to use
COMPOSE_FILES="-f docker-compose.yml"

if [ "$1" = "production" ]; then
    echo "🏭 Starting in PRODUCTION mode..."
    COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.production.yml"
elif [ "$1" = "dev" ] || [ "$1" = "development" ]; then
    echo "🛠️  Starting in DEVELOPMENT mode..."
    COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.override.yml"
else
    echo "📦 Starting in DEFAULT mode..."
    echo "💡 Use './start.sh dev' for development or './start.sh production' for production"
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p ../seed/contracts
mkdir -p logs/{backend,hangfire,nginx}

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local health_check=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if eval $health_check; then
            echo "✅ $service_name is ready!"
            return 0
        fi

        echo "🔄 Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 10
        attempt=$((attempt + 1))
    done

    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Start the infrastructure services first
echo "🗄️  Starting infrastructure services..."
docker-compose $COMPOSE_FILES up -d postgres elasticsearch redis minio mailhog

# Wait for infrastructure services
wait_for_service "PostgreSQL" "docker-compose $COMPOSE_FILES exec -T postgres pg_isready -U postgres"
wait_for_service "Elasticsearch" "curl -sf http://localhost:9200/_cluster/health"
wait_for_service "MinIO" "curl -sf http://localhost:9000/minio/health/live"
wait_for_service "Redis" "docker-compose $COMPOSE_FILES exec -T redis redis-cli ping"

# Initialize infrastructure
echo "🔧 Initializing infrastructure..."
chmod +x init-scripts/*.sh

# Initialize Elasticsearch indices
echo "📊 Setting up Elasticsearch indices..."
docker run --rm --network enova_enova-network curlimages/curl:latest \
    /bin/sh -c "cd / && $(cat init-scripts/01-init-elasticsearch.sh)"

# Initialize MinIO buckets
echo "🪣 Setting up MinIO buckets..."
docker run --rm --network enova_enova-network minio/mc:latest \
    /bin/sh -c "$(cat init-scripts/02-init-minio.sh)"

# Start AI service
echo "🤖 Starting AI service..."
docker-compose $COMPOSE_FILES up -d ai
wait_for_service "AI Service" "curl -sf http://localhost:8000/health"

# Start backend services
echo "🖥️  Starting backend services..."
docker-compose $COMPOSE_FILES up -d backend hangfire

# Run database migrations and seed data
echo "📚 Running database migrations and seeding data..."
docker-compose $COMPOSE_FILES up init
wait_for_service "Backend API" "curl -sf http://localhost:5000/health"

# Start frontend
echo "🌐 Starting frontend..."
docker-compose $COMPOSE_FILES up -d frontend
wait_for_service "Frontend" "curl -sf http://localhost:4200"

# Start additional services for production
if [ "$1" = "production" ]; then
    echo "🔍 Starting monitoring services..."
    docker-compose $COMPOSE_FILES up -d nginx prometheus grafana fluentd
fi

# Show service status
echo ""
echo "🎉 Enova Contract Intelligence Platform is now running!"
echo ""
echo "📱 Application URLs:"
echo "   Frontend:     http://localhost:4200"
echo "   Backend API:  http://localhost:5000"
echo "   Swagger:      http://localhost:5000/swagger"
echo "   AI Service:   http://localhost:8000"
echo "   Hangfire:     http://localhost:7080"
echo ""
echo "🔧 Management URLs:"
echo "   MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo "   MailHog:       http://localhost:8025"
echo "   Elasticsearch: http://localhost:9200"

if [ "$1" = "dev" ] || [ "$1" = "development" ]; then
    echo "   Adminer:       http://localhost:8080"
    echo "   ES Head:       http://localhost:9100"
    echo "   Redis Cmd:     http://localhost:8081"
fi

if [ "$1" = "production" ]; then
    echo "   Prometheus:    http://localhost:9090"
    echo "   Grafana:       http://localhost:3000 (admin/admin)"
fi

echo ""
echo "👤 Default Login Credentials:"
echo "   Admin:        admin@enova.local / Admin!234"
echo "   Manager:      manager@enova.local / Manager!234"
echo "   Subcontractor: sub@enova.local / Sub!234"
echo ""
echo "📖 For more information, see the README.md file"
echo "🛑 To stop all services: docker-compose $COMPOSE_FILES down"
echo ""

# Show logs for main services
if [ "$2" = "logs" ]; then
    echo "📋 Showing live logs (Ctrl+C to exit)..."
    docker-compose $COMPOSE_FILES logs -f backend frontend ai
fi