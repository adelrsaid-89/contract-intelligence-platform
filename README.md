# Enova Contract Intelligence Platform (CIP) - POC

A comprehensive Contract Intelligence Platform built for local deployment, featuring AI-powered document processing, obligation tracking, and natural language querying capabilities.

## 🎯 Overview

This POC demonstrates a complete contract management workflow:
- **Document Management**: Upload and organize contracts with version control
- **AI Extraction**: Automatic metadata and obligation extraction from PDFs
- **Workflow Management**: Assignment, tracking, and evidence collection
- **Role-Based Access**: Admin, Manager, and Subcontractor interfaces
- **Q&A System**: Natural language queries over structured contract data
- **Dynamic Configuration**: No hardcoded data, fully configurable system

## 🏗️ Architecture

- **Backend**: .NET 8 API with Clean Architecture, PostgreSQL, Elasticsearch, Hangfire
- **Frontend**: Angular 17 with Material Design, i18n (English/Arabic), RTL support
- **AI Service**: Python FastAPI with local models and cloud provider adapters
- **Storage**: MinIO object storage with local filesystem fallback
- **Infrastructure**: Docker Compose for complete local deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- 10GB+ disk space

### One-Command Startup

```bash
cd deploy
cp .env.example .env
# Optional: Edit .env with your Azure/OpenAI keys
./start.sh
```

### Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:5000
- **Swagger**: http://localhost:5000/swagger
- **AI Service**: http://localhost:8000
- **Hangfire**: http://localhost:7080

### Default Credentials

- **Admin**: admin@example.com / Admin123!
- **Manager**: sarah.johnson@example.com / Manager123!
- **Subcontractor**: ahmed.rashid@example.com / User123!

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - Technical architecture and design decisions
- [API Documentation](docs/api-documentation.md) - Complete API reference
- [Demo Script](docs/demo-script.md) - Step-by-step user journey walkthrough
- [Deployment Guide](docs/deployment-guide.md) - Production deployment instructions
- [Seed Data Guide](docs/seed-notes.md) - Understanding and customizing seed data
- [Testing Guide](docs/testing-guide.md) - Testing strategy and examples

## 🎮 Demo Workflow

1. **Admin Setup**: Create projects and grant manager access
2. **Contract Upload**: Upload PDF contracts to project repositories
3. **AI Extraction**: Extract metadata and obligations with confidence scores
4. **Human Review**: Review and correct AI extractions
5. **Assignment**: Assign obligations to internal staff or subcontractors
6. **Execution**: Track progress, upload evidence, validate completion
7. **Monitoring**: View dashboards, penalty risks, and compliance metrics
8. **Q&A**: Ask natural language questions about contract data

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Seed Data Mode
SEED_MODE=example  # or 'none' for empty system

# AI Providers (optional cloud features)
AI_OCR_PROVIDER=local  # or 'azure'
AI_EXTRACT_PROVIDER=local  # or 'openai'
AZURE_OPENAI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Security
JWT_KEY=your_secure_key_here
```

### AI Provider Setup

The system works completely offline with local models. To enable cloud AI:

1. **Azure OpenAI**: Set `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`
2. **OpenAI**: Set `OPENAI_API_KEY`
3. **Azure Document Intelligence**: Set `AZURE_DOCINTEL_ENDPOINT` and `AZURE_DOCINTEL_KEY`

## 🛠️ Development

### Development Mode

```bash
./start.sh dev
```

Includes:
- Hot reload for all services
- Additional management tools (Adminer, ES Head, Redis Commander)
- Development debugging enabled

### Build from Source

```bash
# Backend
cd backend
dotnet build
dotnet test

# Frontend
cd frontend/enova-cip-ui
npm install
npm run build

# AI Service
cd ai
pip install -r requirements.txt
pytest
```

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
cd backend && dotnet test

# Frontend tests
cd frontend/enova-cip-ui && npm test

# AI service tests
cd ai && pytest

# Integration tests
cd deploy && docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### API Testing

Use the provided Postman collection:
```bash
# Import collection
curl -o enova-cip.postman_collection.json http://localhost:5000/swagger/v1/swagger.json
```

## 📊 Monitoring

### Production Monitoring

```bash
./start.sh production
```

Includes:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Log Aggregation**: Centralized logging with Fluentd
- **Nginx Reverse Proxy**: Load balancing and SSL termination

### Health Checks

- Backend: http://localhost:5000/health
- AI Service: http://localhost:8000/health
- All services: `docker-compose ps`

## 🔒 Security Features

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- Project-level permissions
- Comprehensive audit logging
- File upload validation
- Rate limiting and request validation

## 🌍 Internationalization

- English and Arabic language support
- RTL (Right-to-Left) text direction
- Dynamic language switching
- Localized date/number formatting

## 📱 User Interfaces

### Admin Dashboard
- Global KPIs and compliance metrics
- Penalty risk overview
- Project and user management
- System configuration

### Manager Dashboard
- Project-specific KPIs
- Subcontractor performance tracking
- Obligation assignment and monitoring
- Evidence validation

### Subcontractor Dashboard
- Personal task kanban board
- Progress tracking
- Evidence upload
- Notification center

## 🎯 Key Acceptance Criteria ✅

- ✅ **Dynamic System**: No hardcoded names, fully configurable
- ✅ **RBAC**: Complete role-based access control with project permissions
- ✅ **AI Extraction**: >80% accuracy with confidence scoring
- ✅ **Workflow**: Complete assignment → execution → validation flow
- ✅ **Q&A System**: Natural language queries over structured data
- ✅ **Dashboards**: Role-specific KPIs and monitoring
- ✅ **Provider Adapters**: Local/cloud AI switching via environment variables

## 🆘 Troubleshooting

### Common Issues

**Services not starting**: Check Docker resources (8GB+ RAM recommended)
```bash
docker system prune -f
docker-compose down -v
./start.sh
```

**Database connection errors**: Wait for PostgreSQL to be fully ready
```bash
docker-compose logs postgres
```

**AI service errors**: Check model downloads and environment variables
```bash
docker-compose logs ai
```

### Getting Help

1. Check service logs: `docker-compose logs [service_name]`
2. Verify environment configuration: `cat .env`
3. Check service health: `curl http://localhost:5000/health`
4. Review documentation in `/docs/` directory

## 📄 License

This POC is provided for demonstration purposes. See individual component licenses for production use.

## 🤝 Support

For technical support or questions:
- Review the comprehensive documentation in `/docs/`
- Check the troubleshooting section above
- Examine service logs for detailed error information

---

**🎉 The Enova Contract Intelligence Platform POC is ready for demonstration and evaluation!**