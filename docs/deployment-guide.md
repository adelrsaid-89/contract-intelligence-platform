# Deployment Guide - Contract Intelligence Platform

This comprehensive deployment guide covers development, staging, and production deployment scenarios for the Contract Intelligence Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Production Deployment](#kubernetes-production-deployment)
5. [Azure Cloud Deployment](#azure-cloud-deployment)
6. [Database Management](#database-management)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security Configuration](#security-configuration)
10. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Development Environment:**
- Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
- 16GB RAM minimum (32GB recommended)
- 100GB available disk space
- Docker Desktop 4.0+

**Production Environment:**
- Linux-based servers (Ubuntu 20.04 LTS recommended)
- Kubernetes cluster (1.24+) or Docker Swarm
- Load balancer (Nginx, Azure Load Balancer, or AWS ALB)
- SSL certificates

### Software Dependencies

**Backend:**
- .NET 8.0 SDK
- SQL Server 2019+ or Azure SQL Database
- Redis for caching

**Frontend:**
- Node.js 18.x LTS
- npm 9.x or yarn 3.x

**AI Services:**
- Python 3.9+
- Azure OpenAI or OpenAI API access
- Azure Document Intelligence (optional)

**Infrastructure:**
- Docker 24.0+
- Kubernetes 1.24+ (for production)
- Helm 3.8+ (for Kubernetes deployments)

## Development Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/enova-cip.git
cd enova-cip
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Restore packages
dotnet restore

# Set up user secrets for development
dotnet user-secrets init --project Enova.Cip.Api
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Server=(localdb)\\mssqllocaldb;Database=EnovaCIP_Dev;Trusted_Connection=true;" --project Enova.Cip.Api
dotnet user-secrets set "JwtSettings:Secret" "your-super-secret-jwt-key-that-is-at-least-32-characters-long" --project Enova.Cip.Api
dotnet user-secrets set "AzureOpenAI:Endpoint" "https://your-openai.openai.azure.com/" --project Enova.Cip.Api
dotnet user-secrets set "AzureOpenAI:ApiKey" "your-azure-openai-key" --project Enova.Cip.Api

# Run migrations
dotnet ef database update --project Enova.Cip.Infrastructure --startup-project Enova.Cip.Api

# Seed database
sqlcmd -S "(localdb)\\mssqllocaldb" -d EnovaCIP_Dev -i ../seed/sql/master-seed.sql

# Run backend
dotnet run --project Enova.Cip.Api
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend/enova-cip-ui

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your settings
cat > .env.local << EOF
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_APP_NAME=Contract Intelligence Platform
EOF

# Run frontend
npm run dev
```

### 4. AI Services Setup

```bash
# Navigate to AI services
cd ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your settings
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-ai.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-doc-intelligence-key
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Run AI services
python app.py
```

### 5. Verify Development Setup

```bash
# Check all services are running
curl http://localhost:5000/api/health      # Backend API
curl http://localhost:3000                 # Frontend
curl http://localhost:8000/health          # AI Services

# Run initial tests
cd backend && dotnet test
cd ../frontend/enova-cip-ui && npm test
```

## Docker Deployment

### 1. Development with Docker Compose

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'

services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      - SA_PASSWORD=DevPassword123!
      - ACCEPT_EULA=Y
      - MSSQL_PID=Express
    ports:
      - "1433:1433"
    volumes:
      - sqlserver_data:/var/opt/mssql
    healthcheck:
      test: /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P DevPassword123! -Q "SELECT 1"
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: redis-cli ping
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "5000:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=EnovaCIP;User Id=sa;Password=DevPassword123!;TrustServerCertificate=true;
      - Redis__ConnectionString=redis:6379
      - JwtSettings__Secret=your-super-secret-jwt-key-that-is-at-least-32-characters-long
    depends_on:
      sqlserver:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./seed/contracts:/app/wwwroot/contracts

  frontend:
    build:
      context: ./frontend/enova-cip-ui
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
      - NEXT_PUBLIC_ENVIRONMENT=development
    volumes:
      - ./frontend/enova-cip-ui:/app
      - /app/node_modules

  ai-services:
    build:
      context: ./ai
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
    volumes:
      - ./ai:/app
      - ./seed/contracts:/app/data/contracts

volumes:
  sqlserver_data:
  redis_data:

networks:
  default:
    name: enova-cip-network
```

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    expose:
      - "80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ConnectionStrings__DefaultConnection=${DATABASE_CONNECTION_STRING}
      - Redis__ConnectionString=${REDIS_CONNECTION_STRING}
      - JwtSettings__Secret=${JWT_SECRET}
      - AzureOpenAI__Endpoint=${AZURE_OPENAI_ENDPOINT}
      - AzureOpenAI__ApiKey=${AZURE_OPENAI_KEY}
      - Logging__LogLevel__Default=Information
    restart: unless-stopped
    healthcheck:
      test: curl -f http://localhost/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend/enova-cip-ui
      dockerfile: Dockerfile
    expose:
      - "3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=${API_BASE_URL}
      - NEXT_PUBLIC_ENVIRONMENT=production
    restart: unless-stopped

  ai-services:
    build:
      context: ./ai
      dockerfile: Dockerfile
    expose:
      - "8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - PYTHONPATH=/app
    restart: unless-stopped
    healthcheck:
      test: curl -f http://localhost:8000/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    name: enova-cip-production
```

### 3. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:80;
    }

    upstream frontend {
        server frontend:3000;
    }

    upstream ai-services {
        server ai-services:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/certificate.pem;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # CORS headers (if needed)
            add_header Access-Control-Allow-Origin $http_origin;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type";
        }

        # Auth endpoints (stricter rate limiting)
        location /api/auth/ {
            limit_req zone=auth burst=5 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # AI services
        location /ai/ {
            proxy_pass http://ai-services/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Increase timeouts for AI processing
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # File uploads
        location /api/files {
            client_max_body_size 100M;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Deploy with Docker Compose

```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose logs -f backend

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Kubernetes Production Deployment

### 1. Namespace and ConfigMaps

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: enova-cip
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: enova-cip
data:
  ASPNETCORE_ENVIRONMENT: "Production"
  Logging__LogLevel__Default: "Information"
  NEXT_PUBLIC_ENVIRONMENT: "production"
```

### 2. Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: enova-cip
type: Opaque
data:
  DATABASE_CONNECTION_STRING: <base64-encoded-connection-string>
  JWT_SECRET: <base64-encoded-jwt-secret>
  AZURE_OPENAI_KEY: <base64-encoded-openai-key>
  REDIS_CONNECTION_STRING: <base64-encoded-redis-connection>
```

### 3. Database Deployment

```yaml
# k8s/sqlserver.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: sqlserver
  namespace: enova-cip
spec:
  serviceName: sqlserver-service
  replicas: 1
  selector:
    matchLabels:
      app: sqlserver
  template:
    metadata:
      labels:
        app: sqlserver
    spec:
      containers:
      - name: sqlserver
        image: mcr.microsoft.com/mssql/server:2019-latest
        env:
        - name: SA_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: SA_PASSWORD
        - name: ACCEPT_EULA
          value: "Y"
        ports:
        - containerPort: 1433
        volumeMounts:
        - name: sqlserver-storage
          mountPath: /var/opt/mssql
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
  volumeClaimTemplates:
  - metadata:
      name: sqlserver-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: sqlserver-service
  namespace: enova-cip
spec:
  selector:
    app: sqlserver
  ports:
  - port: 1433
    targetPort: 1433
  type: ClusterIP
```

### 4. Redis Deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: enova-cip
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: enova-cip
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: enova-cip
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### 5. Backend API Deployment

```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: enova-cip
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/enova-cip-backend:latest
        ports:
        - containerPort: 80
        env:
        - name: ConnectionStrings__DefaultConnection
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_CONNECTION_STRING
        - name: Redis__ConnectionString
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: REDIS_CONNECTION_STRING
        - name: JwtSettings__Secret
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: JWT_SECRET
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: enova-cip
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### 6. Frontend Deployment

```yaml
# k8s/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: enova-cip
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/enova-cip-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_BASE_URL
          value: "https://your-domain.com/api"
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: enova-cip
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

### 7. Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: enova-cip
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: app-tls-secret
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
```

### 8. Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n enova-cip
kubectl get services -n enova-cip
kubectl get ingress -n enova-cip

# View logs
kubectl logs -f deployment/backend -n enova-cip
kubectl logs -f deployment/frontend -n enova-cip

# Scale deployments
kubectl scale deployment backend --replicas=5 -n enova-cip

# Rolling update
kubectl set image deployment/backend backend=your-registry/enova-cip-backend:v2.0.0 -n enova-cip
```

## Azure Cloud Deployment

### 1. Azure Resources Setup

```bash
# Create resource group
az group create --name enova-cip-rg --location eastus

# Create Azure SQL Database
az sql server create \
  --name enova-cip-sql-server \
  --resource-group enova-cip-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password ComplexPassword123!

az sql db create \
  --resource-group enova-cip-rg \
  --server enova-cip-sql-server \
  --name EnovaCIP \
  --service-objective S2

# Create Azure Cache for Redis
az redis create \
  --location eastus \
  --resource-group enova-cip-rg \
  --name enova-cip-redis \
  --sku Standard \
  --vm-size c1

# Create Azure Container Registry
az acr create \
  --resource-group enova-cip-rg \
  --name enovacipregistry \
  --sku Basic \
  --admin-enabled true

# Create AKS cluster
az aks create \
  --resource-group enova-cip-rg \
  --name enova-cip-aks \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --attach-acr enovacipregistry
```

### 2. Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop

variables:
  containerRegistry: 'enovacipregistry.azurecr.io'
  imageRepository: 'enova-cip'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'

stages:
- stage: Build
  displayName: Build and push stage
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: ubuntu-latest
    steps:
    - task: Docker@2
      displayName: Build and push backend image
      inputs:
        command: buildAndPush
        repository: $(imageRepository)-backend
        dockerfile: backend/Dockerfile
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

    - task: Docker@2
      displayName: Build and push frontend image
      inputs:
        command: buildAndPush
        repository: $(imageRepository)-frontend
        dockerfile: frontend/enova-cip-ui/Dockerfile
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: Deploy
    displayName: Deploy
    pool:
      vmImage: ubuntu-latest
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: KubernetesManifest@0
            displayName: Deploy to Kubernetes cluster
            inputs:
              action: deploy
              manifests: |
                k8s/configmap.yaml
                k8s/secrets.yaml
                k8s/backend.yaml
                k8s/frontend.yaml
                k8s/ingress.yaml
```

## Database Management

### 1. Migration Scripts

```bash
# Create migration
dotnet ef migrations add InitialCreate --project Enova.Cip.Infrastructure --startup-project Enova.Cip.Api

# Apply migrations to production
dotnet ef database update --project Enova.Cip.Infrastructure --startup-project Enova.Cip.Api --connection "Server=your-server;Database=EnovaCIP;..."

# Generate SQL script for manual deployment
dotnet ef migrations script --project Enova.Cip.Infrastructure --startup-project Enova.Cip.Api --output migration.sql
```

### 2. Database Backup Strategy

```sql
-- Automated backup script
BACKUP DATABASE [EnovaCIP]
TO DISK = N'/backup/EnovaCIP_Full_$(date).bak'
WITH FORMAT,
     INIT,
     COMPRESSION,
     STATS = 10,
     CHECKSUM;

-- Point-in-time recovery backup
BACKUP LOG [EnovaCIP]
TO DISK = N'/backup/EnovaCIP_Log_$(datetime).trn'
WITH COMPRESSION, STATS = 10;
```

### 3. Database Monitoring

```sql
-- Performance monitoring queries
SELECT
    DB_NAME(database_id) as DatabaseName,
    SUM(user_seeks + user_scans + user_lookups) as TotalReads,
    SUM(user_updates) as TotalWrites,
    SUM(user_seeks + user_scans + user_lookups + user_updates) as TotalIO
FROM sys.dm_db_index_usage_stats
WHERE database_id = DB_ID('EnovaCIP')
GROUP BY database_id;

-- Index fragmentation check
SELECT
    OBJECT_NAME(ips.object_id) as TableName,
    i.name as IndexName,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'SAMPLED') ips
JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
WHERE ips.avg_fragmentation_in_percent > 10
ORDER BY ips.avg_fragmentation_in_percent DESC;
```

## Environment Configuration

### 1. Environment Variables

```bash
# Production environment variables
export ASPNETCORE_ENVIRONMENT=Production
export ConnectionStrings__DefaultConnection="Server=prod-server;Database=EnovaCIP;User Id=app_user;Password=secure_password;Encrypt=true;"
export Redis__ConnectionString="prod-redis:6379"
export JwtSettings__Secret="production-jwt-secret-key-32-chars-minimum"
export JwtSettings__Issuer="https://your-domain.com"
export JwtSettings__Audience="enova-cip-users"
export JwtSettings__ExpiryMinutes=60

# Azure OpenAI Configuration
export AzureOpenAI__Endpoint="https://your-openai.openai.azure.com/"
export AzureOpenAI__ApiKey="your-production-openai-key"
export AzureOpenAI__DeploymentName="gpt-4"

# File Storage Configuration
export FileStorage__Type="AzureBlob"  # or "Local"
export FileStorage__AzureBlob__ConnectionString="your-blob-storage-connection"
export FileStorage__AzureBlob__ContainerName="enova-cip-files"

# Logging Configuration
export Logging__LogLevel__Default=Information
export Logging__LogLevel__Microsoft=Warning
export Logging__ApplicationInsights__InstrumentationKey="your-app-insights-key"

# Security Configuration
export Security__RequireHttps=true
export Security__AllowedOrigins="https://your-domain.com"
export Security__EnableCors=true
```

### 2. Configuration Validation

```csharp
// Startup configuration validation
public void ConfigureServices(IServiceCollection services)
{
    // Validate configuration on startup
    services.Configure<JwtSettings>(Configuration.GetSection("JwtSettings"));
    services.Configure<AzureOpenAISettings>(Configuration.GetSection("AzureOpenAI"));

    services.PostConfigure<JwtSettings>(settings =>
    {
        if (string.IsNullOrEmpty(settings.Secret) || settings.Secret.Length < 32)
            throw new InvalidOperationException("JWT Secret must be at least 32 characters long");
    });
}
```

## Monitoring and Logging

### 1. Application Insights Configuration

```csharp
// Program.cs
builder.Services.AddApplicationInsightsTelemetry(builder.Configuration);

// Custom telemetry
builder.Services.AddSingleton<ITelemetryInitializer, CustomTelemetryInitializer>();

public class CustomTelemetryInitializer : ITelemetryInitializer
{
    public void Initialize(ITelemetry telemetry)
    {
        telemetry.Context.GlobalProperties["Application"] = "EnovaCIP";
        telemetry.Context.GlobalProperties["Environment"] = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT");
    }
}
```

### 2. Structured Logging with Serilog

```csharp
// Program.cs
builder.Host.UseSerilog((context, configuration) =>
{
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "EnovaCIP")
        .WriteTo.Console()
        .WriteTo.File("logs/app-.txt", rollingInterval: RollingInterval.Day)
        .WriteTo.ApplicationInsights(TelemetryConfiguration.CreateDefault(), TelemetryConverter.Traces);
});
```

### 3. Health Checks

```csharp
// Configure health checks
builder.Services.AddHealthChecks()
    .AddSqlServer(connectionString, tags: new[] { "database" })
    .AddRedis(redisConnectionString, tags: new[] { "cache" })
    .AddUrlGroup(new Uri($"{aiServiceUrl}/health"), "ai-service", tags: new[] { "ai" });

// Health check endpoint
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```

### 4. Prometheus Metrics

```csharp
// Add metrics
builder.Services.AddSingleton<DiagnosticSource, DiagnosticListener>(
    provider => new DiagnosticListener("EnovaCIP"));

// Custom metrics middleware
public class MetricsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly Counter _requestCounter;
    private readonly Histogram _requestDuration;

    public MetricsMiddleware(RequestDelegate next)
    {
        _next = next;
        _requestCounter = Metrics.CreateCounter("http_requests_total", "Total HTTP requests", "method", "endpoint");
        _requestDuration = Metrics.CreateHistogram("http_request_duration_seconds", "HTTP request duration");
    }

    public async Task InvokeAsync(HttpContext context)
    {
        using var timer = _requestDuration.NewTimer();
        await _next(context);

        _requestCounter.WithTags(context.Request.Method, context.Request.Path).Inc();
    }
}
```

## Security Configuration

### 1. SSL/TLS Configuration

```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout private.key -out certificate.pem -days 365 -nodes

# Let's Encrypt for production
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

### 2. Security Headers

```csharp
// Security middleware
public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    app.UseSecurityHeaders(policies =>
    {
        policies.AddFrameOptionsDeny()
                .AddXssProtectionBlock()
                .AddContentTypeOptionsNoSniff()
                .AddStrictTransportSecurityMaxAgeIncludeSubDomains(maxAgeInSeconds: 60 * 60 * 24 * 365)
                .AddReferrerPolicyStrictOriginWhenCrossOrigin()
                .RemoveServerHeader();
    });
}
```

### 3. API Rate Limiting

```csharp
// Rate limiting configuration
builder.Services.Configure<IpRateLimitOptions>(builder.Configuration.GetSection("IpRateLimiting"));
builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();

// Rate limiting rules in appsettings.json
{
  "IpRateLimiting": {
    "EnableEndpointRateLimiting": true,
    "StackBlockedRequests": false,
    "RealIpHeader": "X-Real-IP",
    "ClientIdHeader": "X-ClientId",
    "GeneralRules": [
      {
        "Endpoint": "/api/auth/*",
        "Period": "1m",
        "Limit": 5
      },
      {
        "Endpoint": "/api/*",
        "Period": "1h",
        "Limit": 1000
      }
    ]
  }
}
```

## Backup and Disaster Recovery

### 1. Database Backup Strategy

```bash
#!/bin/bash
# backup-script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="EnovaCIP"

# Full backup (daily)
if [ $(date +%H) -eq 02 ]; then
    sqlcmd -S $DB_SERVER -U $DB_USER -P $DB_PASSWORD -Q "
    BACKUP DATABASE [$DB_NAME]
    TO DISK = N'$BACKUP_DIR/${DB_NAME}_Full_$DATE.bak'
    WITH FORMAT, INIT, COMPRESSION, STATS = 10, CHECKSUM;"
fi

# Transaction log backup (every 15 minutes)
sqlcmd -S $DB_SERVER -U $DB_USER -P $DB_PASSWORD -Q "
BACKUP LOG [$DB_NAME]
TO DISK = N'$BACKUP_DIR/${DB_NAME}_Log_$DATE.trn'
WITH COMPRESSION, STATS = 10;"

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.bak" -mtime +30 -delete
find $BACKUP_DIR -name "*.trn" -mtime +7 -delete
```

### 2. Application Backup

```bash
#!/bin/bash
# app-backup.sh

# Backup application files
tar -czf /backups/app_$(date +%Y%m%d).tar.gz \
    /app/uploads \
    /app/config \
    /app/logs

# Backup to cloud storage
aws s3 cp /backups/ s3://enova-cip-backups/ --recursive
```

### 3. Disaster Recovery Plan

```yaml
# disaster-recovery.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dr-procedures
data:
  recovery-steps: |
    1. Assess the scope of the disaster
    2. Activate disaster recovery team
    3. Restore database from latest backup
    4. Deploy application to DR environment
    5. Update DNS to point to DR environment
    6. Verify application functionality
    7. Communicate status to stakeholders
    8. Plan failback once primary is restored
```

## Troubleshooting

### 1. Common Issues and Solutions

#### Database Connection Issues

```bash
# Test database connectivity
sqlcmd -S server -U username -P password -Q "SELECT 1"

# Check connection string format
Server=server;Database=database;User Id=user;Password=password;Encrypt=true;TrustServerCertificate=false;

# Verify firewall rules
telnet server-name 1433
```

#### Authentication Problems

```bash
# Verify JWT configuration
echo $JWT_SECRET | wc -c  # Should be >= 32

# Check token expiration
jwt-cli decode <token>

# Validate issuer/audience
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/user/profile
```

#### Performance Issues

```sql
-- Find slow queries
SELECT TOP 10
    qs.total_elapsed_time / qs.execution_count as avg_elapsed_time,
    qs.execution_count,
    SUBSTRING(qt.text, qs.statement_start_offset/2,
        (CASE WHEN qs.statement_end_offset = -1
        THEN LEN(CONVERT(nvarchar(MAX), qt.text)) * 2
        ELSE qs.statement_end_offset END - qs.statement_start_offset)/2) as query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY avg_elapsed_time DESC;
```

### 2. Debug Mode Configuration

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.AspNetCore": "Debug",
      "Microsoft.EntityFrameworkCore": "Debug"
    }
  },
  "EnableDetailedErrors": true,
  "EnableDeveloperExceptionPage": true
}
```

### 3. Monitoring Commands

```bash
# Check application health
curl -f http://localhost:5000/health || echo "Health check failed"

# Monitor resource usage
docker stats

# View application logs
kubectl logs -f deployment/backend -n enova-cip --tail=100

# Check database performance
docker exec -it sqlserver sqlcmd -S localhost -U sa -P password -Q "
SELECT
    DB_NAME() as database_name,
    COUNT(*) as active_connections
FROM sys.dm_exec_sessions
WHERE is_user_process = 1"
```

### 4. Emergency Procedures

```bash
# Emergency shutdown
kubectl scale deployment backend --replicas=0 -n enova-cip

# Emergency database failover
# (Specific steps depend on your database setup)

# Emergency rollback
kubectl rollout undo deployment/backend -n enova-cip

# Check rollback status
kubectl rollout status deployment/backend -n enova-cip
```

This deployment guide provides comprehensive instructions for deploying the Contract Intelligence Platform across different environments while maintaining security, performance, and reliability standards.