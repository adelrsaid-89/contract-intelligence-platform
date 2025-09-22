# AI Operations Microservice

A comprehensive FastAPI microservice for AI-powered document operations including OCR, metadata extraction, obligation extraction, and Q&A RAG system.

## Features

### OCR (Optical Character Recognition)
- **Local OCR**: Tesseract-based text extraction
- **Azure Document Intelligence**: Cloud-based OCR with advanced layout analysis
- **Supported formats**: PDF, PNG, JPG, JPEG, TIFF, BMP
- **Layout extraction**: Paragraphs, lines, tables with bounding boxes
- **Multi-language support**: 50+ languages

### Metadata Extraction
- **Local extraction**: Transformer-based models (LayoutLMv3)
- **OpenAI/Azure OpenAI**: GPT-powered extraction
- **Supported fields**: ProjectName, ClientName, ContractValue, StartDate, EndDate, Country, PaymentTerms, Services, KPIs, SLAs, PenaltyClauses
- **Confidence scoring**: Each field includes confidence scores
- **Text offsets**: Precise location tracking in source documents

### Obligation Extraction
- **Smart detection**: Identifies contractual obligations using keywords and patterns
- **Structured output**: Description, Frequency, DueDate, PenaltyText
- **Categorization**: Automatic categorization (reporting, maintenance, delivery, compliance, payment, performance)
- **Both local and cloud**: Supports local models and OpenAI

### Q&A RAG System
- **FAISS indexing**: Vector-based document search
- **Multiple search modes**: Semantic, keyword, and hybrid search
- **Advanced filtering**: Project, contractor, status, date range filters
- **Answer generation**: AI-powered answer synthesis from multiple sources
- **Deep linking**: Direct links to source document locations

### Storage Integration
- **MinIO support**: Object storage for documents
- **Local filesystem**: Fallback storage option
- **Unified interface**: Seamless switching between storage backends

## Installation

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (recommended)
- Tesseract OCR
- PostgreSQL (optional, for structured data)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ai

# Copy environment configuration
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng poppler-utils

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\\Scripts\\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create data directories
mkdir -p data faiss_index logs

# Copy environment configuration
cp .env.example .env

# Start the service
uvicorn main:app --reload
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# AI Provider Configuration
AI_OCR_PROVIDER=local          # local, azure
AI_EXTRACT_PROVIDER=local      # local, openai

# Azure OpenAI (optional)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# OpenAI (optional)
OPENAI_API_KEY=your_key

# Azure Document Intelligence (optional)
AZURE_DOCINTEL_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCINTEL_KEY=your_key

# MinIO Configuration (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Provider Selection

The service automatically selects providers based on configuration:

- **OCR**: Uses Azure if credentials provided, otherwise falls back to local Tesseract
- **Extraction**: Uses OpenAI if API key provided, otherwise uses local transformer models
- **Storage**: Uses MinIO if configured, otherwise uses local filesystem

## API Usage

### OCR Endpoints

#### Extract text from uploaded file
```bash
curl -X POST "http://localhost:8000/ocr/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "languages=eng,spa" \
  -F "extract_layout=true" \
  -F "extract_tables=true"
```

#### Extract from storage
```bash
curl -X POST "http://localhost:8000/ocr/extract-from-storage" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "documents/contract.pdf",
    "provider": "azure",
    "languages": ["eng"]
  }'
```

### Metadata Extraction

#### Extract metadata from text
```bash
curl -X POST "http://localhost:8000/nlp/metadata" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contract text here...",
    "extract_fields": ["ProjectName", "ClientName", "ContractValue"],
    "confidence_threshold": 0.7
  }'
```

### Obligation Extraction

#### Extract obligations
```bash
curl -X POST "http://localhost:8000/nlp/obligations" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The contractor shall deliver monthly reports...",
    "include_penalties": true,
    "confidence_threshold": 0.6
  }'
```

### Q&A System

#### Query documents
```bash
curl -X POST "http://localhost:8000/qa/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What obligations are due this month for project ABC?",
    "filters": {
      "project_id": "ABC",
      "status": "active"
    },
    "max_results": 10,
    "search_mode": "hybrid"
  }'
```

#### Index new documents
```bash
curl -X POST "http://localhost:8000/qa/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "document_id": "doc1",
        "title": "Contract ABC",
        "content": "Document content...",
        "metadata": {
          "project_id": "ABC",
          "contractor": "Company X"
        }
      }
    ],
    "operation": "upsert"
  }'
```

## Example Queries

The Q&A system supports various types of queries:

1. **Obligation queries**:
   - "Obligations due this month for project ABC?"
   - "Who is responsible for maintenance in project XYZ?"

2. **SLA queries**:
   - "SLA for water spillage in project ABC?"
   - "Response time requirements for critical issues?"

3. **Comparison queries**:
   - "Common obligations between project A and project B"
   - "Differences in payment terms across projects"

4. **Status queries**:
   - "Overdue obligations linked to subcontractors"
   - "Completed deliverables for Q4"

## Architecture

### Components

1. **FastAPI Application** (`main.py`): Core application with routing and middleware
2. **Routers** (`routers/`): API endpoint definitions
3. **Services** (`services/`): Business logic for OCR and extraction
4. **RAG System** (`rag/`): FAISS-based indexing and querying
5. **Models** (`models/`): Pydantic schemas for requests/responses
6. **Utilities** (`utils/`): Configuration and storage management

### Data Flow

1. **Document Upload** → **OCR** → **Text Extraction**
2. **Text** → **NLP Services** → **Metadata/Obligations**
3. **Processed Data** → **FAISS Index** → **Searchable Knowledge Base**
4. **User Query** → **Vector Search** → **Answer Generation**

### Storage Layers

- **Object Storage**: MinIO/Local for original documents
- **Vector Index**: FAISS for semantic search
- **Metadata**: PostgreSQL for structured queries (optional)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type checking
mypy .
```

### Adding New Providers

1. Create service class in `services/`
2. Implement required interface methods
3. Add provider configuration to `utils/config.py`
4. Update router to support new provider

## Deployment

### Production Docker

```bash
# Build production image
docker build --target production -t ai-service:latest .

# Run with production settings
docker run -d \
  --name ai-service \
  -p 8000:8000 \
  -e DEBUG=false \
  -e LOG_LEVEL=INFO \
  -v /path/to/data:/app/data \
  ai-service:latest
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests (if provided).

### Health Monitoring

- **Health check**: `GET /health`
- **Provider status**: `GET /providers`
- **Metrics**: `GET /qa/metrics`

## Performance

### Optimization Tips

1. **Use appropriate providers**: Azure/OpenAI for accuracy, local for speed
2. **Batch processing**: Use batch endpoints for multiple documents
3. **Confidence thresholds**: Adjust based on accuracy requirements
4. **FAISS tuning**: Optimize index parameters for your dataset size
5. **Caching**: Enable caching for repeated queries

### Scaling

- **Horizontal**: Run multiple service instances behind load balancer
- **Vertical**: Increase CPU/memory for better model performance
- **Storage**: Use distributed storage (MinIO cluster) for large datasets
- **Database**: Use read replicas for query-heavy workloads

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Install tesseract-ocr package
2. **spaCy model missing**: Run `python -m spacy download en_core_web_sm`
3. **Memory issues**: Reduce batch sizes or increase container memory
4. **API timeouts**: Increase timeout settings for large documents

### Logging

Logs are written to:
- Console (structured JSON in production)
- File: `logs/ai_service.log`

Log levels: DEBUG, INFO, WARNING, ERROR

### Monitoring

Monitor these metrics:
- Response times per endpoint
- OCR processing times
- Extraction accuracy
- FAISS index size and query performance
- Memory and CPU usage

## API Documentation

When the service is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Support

For issues and questions:
- Create GitHub issue
- Check logs for error details
- Review configuration settings
- Verify API key permissions