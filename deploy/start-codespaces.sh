#!/bin/bash
set -e

echo "🚀 Starting Contract Intelligence Platform in GitHub Codespaces..."
echo "======================================================================="

# Check if running in Codespaces
if [ -z "$CODESPACE_NAME" ]; then
    echo "⚠️  This script is designed for GitHub Codespaces environment"
    echo "Use ./start.sh for local Docker deployment instead"
    exit 1
fi

# Update environment variables for Codespaces
echo "🔧 Configuring environment for Codespaces..."
cat > .env << EOF
# Database Configuration
POSTGRES_CONNECTION=Host=localhost;Database=enova_cip;Username=postgres;Password=postgres

# Search Engine
ELASTICSEARCH_URI=http://localhost:9200

# Object Storage
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Email Configuration
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASS=

# AI Service
AI_BASE_URL=http://localhost:8000
AI_OCR_PROVIDER=local
AI_EXTRACT_PROVIDER=local

# JWT Configuration
JWT_ISSUER=enova.codespaces
JWT_AUDIENCE=enova.codespaces
JWT_KEY=SuperSecretCodespacesKey_ChangeInProduction

# Seed Data Configuration
SEED_MODE=example

# Codespaces URLs
FRONTEND_URL=https://$CODESPACE_NAME-4200.app.github.dev
API_BASE_URL=https://$CODESPACE_NAME-5000.app.github.dev
AI_SERVICE_URL=https://$CODESPACE_NAME-8000.app.github.dev

# CORS Configuration
ENABLE_CORS=true
CORS_ORIGINS=https://$CODESPACE_NAME-4200.app.github.dev,https://$CODESPACE_NAME-5000.app.github.dev

# Development Settings
ASPNETCORE_ENVIRONMENT=Development
ASPNETCORE_URLS=http://0.0.0.0:5000
LOG_LEVEL=Information
EOF

echo "✅ Environment configured for Codespaces"

# Start services using Docker Compose
echo "🐳 Starting infrastructure services..."
docker-compose up -d postgres elasticsearch redis minio mailhog

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 5
done
echo "✅ PostgreSQL is ready"

# Check Elasticsearch
echo "🔍 Checking Elasticsearch..."
until curl -sf http://localhost:9200/_cluster/health > /dev/null; do
    echo "Waiting for Elasticsearch..."
    sleep 5
done
echo "✅ Elasticsearch is ready"

# Check MinIO
echo "🔍 Checking MinIO..."
until curl -sf http://localhost:9000/minio/health/live > /dev/null; do
    echo "Waiting for MinIO..."
    sleep 5
done
echo "✅ MinIO is ready"

# Initialize infrastructure
echo "🔧 Initializing infrastructure..."

# Create Elasticsearch indices
curl -X PUT "localhost:9200/contracts_search" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "title": {"type": "text"},
      "content": {"type": "text"}
    }
  }
}' || echo "Contracts index may already exist"

curl -X PUT "localhost:9200/obligations_search" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "description": {"type": "text"},
      "status": {"type": "keyword"}
    }
  }
}' || echo "Obligations index may already exist"

echo "✅ Elasticsearch indices created"

# Start AI service
echo "🤖 Starting AI service..."
cd ../ai
python main.py &
AI_PID=$!
cd ../deploy

# Wait for AI service
echo "⏳ Waiting for AI service..."
sleep 10
until curl -sf http://localhost:8000/health > /dev/null; do
    echo "Waiting for AI service..."
    sleep 5
done
echo "✅ AI service is ready"

# Start backend
echo "🖥️  Starting backend API..."
cd ../backend
dotnet run --project Enova.Cip.Api --urls="http://0.0.0.0:5000" &
BACKEND_PID=$!
cd ../deploy

# Wait for backend
echo "⏳ Waiting for backend API..."
sleep 15
until curl -sf http://localhost:5000/health > /dev/null; do
    echo "Waiting for backend API..."
    sleep 5
done
echo "✅ Backend API is ready"

# Start frontend
echo "🌐 Starting frontend..."
cd ../frontend/enova-cip-ui

# Update environment for Codespaces
cat > src/environments/environment.ts << EOF
export const environment = {
  production: false,
  apiUrl: 'https://$CODESPACE_NAME-5000.app.github.dev',
  aiUrl: 'https://$CODESPACE_NAME-8000.app.github.dev'
};
EOF

ng serve --host 0.0.0.0 --port 4200 --disable-host-check &
FRONTEND_PID=$!
cd ../../deploy

# Wait for frontend
echo "⏳ Waiting for frontend..."
sleep 20
until curl -sf http://localhost:4200 > /dev/null; do
    echo "Waiting for frontend..."
    sleep 5
done
echo "✅ Frontend is ready"

echo ""
echo "🎉 CONTRACT INTELLIGENCE PLATFORM IS NOW RUNNING!"
echo "======================================================================="
echo ""
echo "🌐 ACCESS YOUR APPLICATION:"
echo "   Main App: https://$CODESPACE_NAME-4200.app.github.dev"
echo ""
echo "🔑 LOGIN CREDENTIALS:"
echo "   Admin:        admin@example.com / Admin123!"
echo "   Manager:      sarah.johnson@example.com / Manager123!"
echo "   Subcontractor: ahmed.rashid@example.com / User123!"
echo ""
echo "🛠️  MANAGEMENT INTERFACES:"
echo "   API Docs:     https://$CODESPACE_NAME-5000.app.github.dev/swagger"
echo "   AI Service:   https://$CODESPACE_NAME-8000.app.github.dev"
echo "   Hangfire:     https://$CODESPACE_NAME-7080.app.github.dev"
echo "   MinIO:        https://$CODESPACE_NAME-9001.app.github.dev"
echo "   Email Test:   https://$CODESPACE_NAME-8025.app.github.dev"
echo ""
echo "📋 DEMO WORKFLOW:"
echo "   1. Login as Admin to see global dashboard"
echo "   2. Login as Manager to upload contracts and assign tasks"
echo "   3. Login as Subcontractor to view and complete assignments"
echo "   4. Test AI Q&A with sample questions"
echo ""
echo "⚠️  Keep this terminal open to keep services running"
echo "   To stop: Press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FRONTEND_PID $BACKEND_PID $AI_PID 2>/dev/null || true
    docker-compose down
    echo "✅ All services stopped"
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Wait for user interruption
echo "✨ Application ready! Click the Frontend link above to start using the app"
echo "   Press Ctrl+C to stop all services"
echo ""

# Keep script running
wait