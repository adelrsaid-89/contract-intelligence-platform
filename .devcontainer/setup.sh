#!/bin/bash
set -e

echo "🚀 Setting up Contract Intelligence Platform in GitHub Codespaces..."
echo "This will take about 5-10 minutes..."

# Update system
sudo apt-get update

# Install additional dependencies
sudo apt-get install -y curl wget unzip

# Install .NET SDK if not present
if ! command -v dotnet &> /dev/null; then
    echo "Installing .NET 8 SDK..."
    wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    sudo apt-get update
    sudo apt-get install -y dotnet-sdk-8.0
fi

# Install Node.js and Angular CLI
if ! command -v ng &> /dev/null; then
    echo "Installing Angular CLI..."
    npm install -g @angular/cli
fi

# Install Python dependencies for AI service
echo "Installing Python dependencies..."
cd ai
pip install -r requirements.txt
cd ..

# Install .NET dependencies
echo "Installing .NET dependencies..."
cd backend
dotnet restore
cd ..

# Install Node.js dependencies for frontend
echo "Installing Node.js dependencies..."
cd frontend/enova-cip-ui
npm install
cd ../..

# Set up environment file
echo "Setting up environment configuration..."
cd deploy
cp .env.example .env

# Update .env for Codespaces environment
cat >> .env << 'EOF'

# Codespaces specific configuration
ASPNETCORE_URLS=http://0.0.0.0:5000
API_BASE_URL=https://$CODESPACE_NAME-5000.app.github.dev
AI_BASE_URL=https://$CODESPACE_NAME-8000.app.github.dev
FRONTEND_URL=https://$CODESPACE_NAME-4200.app.github.dev

# Enable CORS for Codespaces
ENABLE_CORS=true
CORS_ORIGINS=https://$CODESPACE_NAME-4200.app.github.dev

# Disable HTTPS redirect in development
ASPNETCORE_ENVIRONMENT=Development
EOF

cd ..

# Make scripts executable
chmod +x deploy/start.sh
chmod +x deploy/start-codespaces.sh

echo "✅ Setup completed!"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Open the terminal in VS Code"
echo "2. Run: cd deploy && ./start-codespaces.sh"
echo "3. Wait 5-10 minutes for all services to start"
echo "4. Click on the 'Frontend (Angular)' port when it appears"
echo ""
echo "🔑 DEFAULT LOGIN CREDENTIALS:"
echo "Admin: admin@example.com / Admin123!"
echo "Manager: sarah.johnson@example.com / Manager123!"
echo "Subcontractor: ahmed.rashid@example.com / User123!"
echo ""
echo "🌐 AVAILABLE SERVICES:"
echo "- Frontend: Port 4200 (main application)"
echo "- Backend API: Port 5000 (with Swagger docs)"
echo "- AI Service: Port 8000"
echo "- Hangfire Dashboard: Port 7080"
echo "- MinIO Console: Port 9001"
echo "- Email Testing: Port 8025"
echo ""