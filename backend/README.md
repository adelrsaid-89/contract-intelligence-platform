# Contract Intelligence Platform - Backend

A comprehensive .NET 8 backend solution for managing contracts, obligations, and assignments with AI-powered data extraction.

## Architecture

This solution follows Clean Architecture principles with the following layers:

- **Domain**: Core business entities and interfaces
- **Infrastructure**: External concerns (database, file storage, email, search)
- **Application**: Business logic and services
- **API**: Web API controllers and middleware
- **Tests**: Unit and integration tests

## Features

### Core Functionality
- **User Management**: Role-based authentication and authorization
- **Project Management**: Project creation with user permission management
- **Contract Management**: File upload, versioning, and metadata extraction
- **Obligation Tracking**: AI-powered obligation extraction and assignment
- **Assignment Management**: Task assignment with progress tracking and evidence upload
- **Notifications**: Email and in-app notifications for reminders and alerts
- **Audit Logging**: Comprehensive audit trail for all actions
- **Search**: Elasticsearch integration for contract and obligation search
- **Risk Assessment**: Penalty risk calculation for overdue obligations

### Security Features
- JWT-based authentication with refresh tokens
- Role-based access control (Admin, Manager, User)
- Project-level permissions (Owner, Manager, Viewer)
- Comprehensive audit logging
- IP address tracking

### Background Jobs
- Assignment email notifications
- Daily reminder notifications (T-14 days to due date)
- Penalty risk calculations for overdue items
- Search index synchronization
- Notification cleanup (90+ days old)

## Technology Stack

- **.NET 8**: Core framework
- **Entity Framework Core**: ORM with PostgreSQL
- **AutoMapper**: Object mapping
- **FluentValidation**: Input validation
- **JWT**: Authentication
- **Hangfire**: Background job processing
- **Serilog**: Structured logging
- **Swagger/OpenAPI**: API documentation
- **MinIO/Local Storage**: File storage
- **Elasticsearch**: Search functionality
- **SMTP**: Email notifications

## Getting Started

### Prerequisites

- .NET 8 SDK
- PostgreSQL database
- (Optional) MinIO for object storage
- (Optional) Elasticsearch for search functionality
- (Optional) SMTP server for email notifications

### Configuration

Update `appsettings.json` with your environment settings:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=cip_db;Username=postgres;Password=password"
  },
  "Jwt": {
    "Secret": "YourSecretKeyThatIsAtLeast32CharactersLong",
    "ExpiryMinutes": 60
  },
  "Storage": {
    "Type": "Local", // or "MinIO"
    "Local": {
      "BasePath": "uploads",
      "BaseUrl": "/files"
    }
  }
}
```

### Database Setup

1. Install Entity Framework Core tools:
```bash
dotnet tool install --global dotnet-ef
```

2. Create and apply migrations:
```bash
cd Enova.Cip.Api
dotnet ef migrations add InitialCreate
dotnet ef database update
```

3. Seed initial data (optional):
```bash
export SEED_MODE=true  # Linux/Mac
set SEED_MODE=true     # Windows
dotnet run
```

### Running the Application

```bash
cd Enova.Cip.Api
dotnet run
```

The API will be available at:
- HTTPS: `https://localhost:7001`
- HTTP: `http://localhost:5001`
- Swagger UI: `https://localhost:7001` (development only)
- Hangfire Dashboard: `https://localhost:7001/hangfire` (admin only)

### Running Tests

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Projects
- `GET /api/project` - Get user's projects
- `GET /api/project/{id}` - Get project details
- `POST /api/project` - Create new project
- `PUT /api/project/{id}` - Update project
- `DELETE /api/project/{id}` - Delete project
- `POST /api/project/{id}/permissions` - Grant user permission
- `DELETE /api/project/{id}/permissions/{userId}` - Revoke permission

### Dashboard
- `GET /api/dashboard` - User dashboard stats
- `GET /api/dashboard/admin` - Admin dashboard stats (admin only)

## Database Schema

### Core Entities
- **Users**: User accounts with roles
- **Projects**: Project containers with client information
- **UserProjectPermissions**: User access levels per project
- **Contracts**: Contract documents with metadata
- **ContractFiles**: File attachments and versions
- **MetadataFields**: Extracted contract metadata
- **Obligations**: Contract obligations and requirements
- **Assignments**: Task assignments to users
- **Evidence**: Assignment completion evidence
- **Notifications**: User notifications
- **PenaltyRisks**: Risk assessments for overdue obligations
- **AuditLogs**: Comprehensive audit trail

## Security Model

### User Roles
- **Admin**: Full system access
- **Manager**: Can manage projects and users
- **User**: Basic access to assigned projects

### Project Permissions
- **Owner**: Full project control including deletion
- **Manager**: Can manage contracts, obligations, and assignments
- **Viewer**: Read-only access to project data

### Authentication Flow
1. User logs in with email/password
2. System returns JWT access token and refresh token
3. Access token used for API calls (1 hour expiry)
4. Refresh token used to get new access tokens
5. All tokens invalidated on logout

## Background Jobs

### Scheduled Jobs
- **Reminder Job**: Daily at 9 AM - sends T-14 day reminders
- **Penalty Risk Job**: Daily at 10 AM - calculates penalty risks
- **Search Indexer**: Hourly - syncs data to Elasticsearch
- **Notification Cleanup**: Weekly - removes old notifications

### Immediate Jobs
- **Assignment Email**: Triggered on assignment creation

## File Storage

### Local Storage
Files stored in configurable local directory with organized folder structure:
```
uploads/
  yyyy/mm/dd/
    {guid}/
      filename.ext
```

### MinIO Storage
Enterprise-grade object storage with:
- Bucket-based organization
- Presigned URLs for secure access
- Automatic retry and error handling

## Error Handling

### Global Exception Middleware
- Catches all unhandled exceptions
- Returns consistent error responses
- Logs errors with correlation IDs
- Maps exception types to HTTP status codes

### Validation
- FluentValidation for input validation
- Custom validation attributes
- Model binding error handling

## Logging

### Serilog Configuration
- Structured logging with JSON format
- Console and file sinks
- Request/response logging middleware
- Performance monitoring

### Log Levels
- **Debug**: Detailed debugging information
- **Information**: General application flow
- **Warning**: Potentially harmful situations
- **Error**: Error events but application continues
- **Fatal**: Very severe error events that might abort application

## Testing

### Unit Tests
- Service layer testing with mocked dependencies
- Domain entity validation
- AutoMapper profile validation
- FluentValidation rule testing

### Integration Tests
- Full API endpoint testing
- Database integration testing
- Authentication flow testing
- File upload/download testing

## Deployment

### Docker Support
The application is containerized with multi-stage builds:

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o /app

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "Enova.Cip.Api.dll"]
```

### Environment Variables
- `ConnectionStrings__DefaultConnection`: Database connection string
- `Jwt__Secret`: JWT signing secret
- `SEED_MODE`: Enable data seeding
- `ASPNETCORE_ENVIRONMENT`: Environment name

## Contributing

1. Follow Clean Architecture principles
2. Write unit tests for new features
3. Update API documentation
4. Follow C# coding conventions
5. Use meaningful commit messages

## License

Proprietary - Enova International, Inc.