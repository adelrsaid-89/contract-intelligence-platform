# API Documentation - Contract Intelligence Platform

## Overview

The Contract Intelligence Platform provides a comprehensive REST API built with .NET 8 and ASP.NET Core. All endpoints are secured with JWT authentication and implement role-based access control (RBAC).

## Base Configuration

### API Base URL
- **Development**: `http://localhost:5000/api`
- **Production**: `https://your-domain.com/api`

### Authentication
All API endpoints (except `/auth/login`) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

### Content Type
All POST/PUT requests should use:
```
Content-Type: application/json
```

## Authentication Endpoints

### POST /api/auth/login

Authenticate a user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "Admin123!"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "refresh-token-string",
  "expiresIn": 3600,
  "user": {
    "id": 1,
    "name": "System Administrator",
    "email": "admin@example.com",
    "role": "Admin"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!"
  }'
```

### POST /api/auth/refresh

Refresh an expired access token using a refresh token.

**Request Body:**
```json
{
  "refreshToken": "refresh-token-string"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "new-jwt-token",
  "refreshToken": "new-refresh-token",
  "expiresIn": 3600
}
```

### POST /api/auth/logout

Invalidate the current session and refresh token.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

## User Management Endpoints

### GET /api/users

Get all users (Admin only) or current user profile.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `pageSize` (int): Items per page (default: 20)
- `role` (string): Filter by role (Admin, Manager, User)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "System Administrator",
      "email": "admin@example.com",
      "role": "Admin",
      "isActive": true,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 20
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:5000/api/users?page=1&pageSize=10" \
  -H "Authorization: Bearer <jwt-token>"
```

### GET /api/users/{id}

Get a specific user by ID.

**Path Parameters:**
- `id` (int): User ID

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "System Administrator",
  "email": "admin@example.com",
  "role": "Admin",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "projectPermissions": [
    {
      "projectId": 1,
      "projectName": "Project Alpha",
      "accessLevel": "Owner"
    }
  ]
}
```

### POST /api/users

Create a new user (Admin only).

**Request Body:**
```json
{
  "name": "New User",
  "email": "new.user@example.com",
  "role": "Manager",
  "password": "TempPassword123!",
  "projectPermissions": [
    {
      "projectId": 1,
      "accessLevel": "Manager"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "name": "New User",
  "email": "new.user@example.com",
  "role": "Manager",
  "isActive": true,
  "createdAt": "2024-01-15T10:30:00Z"
}
```

## Project Management Endpoints

### GET /api/projects

Get all projects accessible to the current user.

**Query Parameters:**
- `status` (string): Filter by status (Active, Closed)
- `country` (string): Filter by country
- `clientName` (string): Filter by client name

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Project Alpha 202401151030",
      "status": "Active",
      "clientName": "National Infrastructure Authority",
      "country": "United Arab Emirates",
      "contractCount": 1,
      "totalValue": 45750000.00,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 20
}
```

### GET /api/projects/{id}

Get detailed project information.

**Path Parameters:**
- `id` (int): Project ID

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Project Alpha 202401151030",
  "status": "Active",
  "clientName": "National Infrastructure Authority",
  "country": "United Arab Emirates",
  "createdAt": "2024-01-15T10:30:00Z",
  "contracts": [
    {
      "id": 1,
      "title": "Transportation Hub Infrastructure Development Contract",
      "value": 45750000.00,
      "startDate": "2024-03-01",
      "endDate": "2027-02-28",
      "status": "Active"
    }
  ],
  "userPermissions": [
    {
      "userId": 1,
      "userName": "System Administrator",
      "accessLevel": "Owner"
    }
  ]
}
```

### POST /api/projects

Create a new project (Admin only).

**Request Body:**
```json
{
  "name": "New Project Name",
  "clientName": "Client Company",
  "country": "United Arab Emirates",
  "managerPermissions": [
    {
      "userId": 2,
      "accessLevel": "Manager"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "New Project Name",
  "status": "Active",
  "clientName": "Client Company",
  "country": "United Arab Emirates",
  "createdAt": "2024-01-15T11:00:00Z"
}
```

## Contract Management Endpoints

### GET /api/contracts

Get all contracts accessible to the current user.

**Query Parameters:**
- `projectId` (int): Filter by project ID
- `status` (string): Filter by status (Draft, Active, Expired, Terminated)
- `startDate` (date): Filter by start date (from)
- `endDate` (date): Filter by end date (to)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Transportation Hub Infrastructure Development Contract",
      "projectId": 1,
      "projectName": "Project Alpha 202401151030",
      "value": 45750000.00,
      "startDate": "2024-03-01",
      "endDate": "2027-02-28",
      "status": "Active",
      "obligationCount": 8,
      "fileCount": 1
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 20
}
```

### GET /api/contracts/{id}

Get detailed contract information.

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Transportation Hub Infrastructure Development Contract",
  "projectId": 1,
  "projectName": "Project Alpha 202401151030",
  "value": 45750000.00,
  "startDate": "2024-03-01",
  "endDate": "2027-02-28",
  "paymentTerms": "Monthly progress payments within 30 days of invoice",
  "status": "Active",
  "metadata": [
    {
      "key": "ContractNumber",
      "value": "TH-2024-001",
      "source": "AI",
      "confidence": 0.99
    }
  ],
  "obligations": [
    {
      "id": 1,
      "description": "Submit comprehensive monthly progress reports...",
      "frequency": "Monthly",
      "dueDate": "2024-02-05",
      "penaltyText": "$10,000 for each day late",
      "source": "AI",
      "confidence": 0.92,
      "assignmentCount": 1
    }
  ],
  "files": [
    {
      "id": 1,
      "fileName": "sample-airport-contract.pdf",
      "fileSize": 1024000,
      "contentType": "application/pdf",
      "uploadedAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /api/contracts

Create a new contract.

**Request Body:**
```json
{
  "projectId": 1,
  "title": "New Contract Title",
  "value": 1000000.00,
  "startDate": "2024-02-01",
  "endDate": "2025-01-31",
  "paymentTerms": "Monthly payments within 30 days"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "title": "New Contract Title",
  "projectId": 1,
  "value": 1000000.00,
  "startDate": "2024-02-01",
  "endDate": "2025-01-31",
  "status": "Draft",
  "createdAt": "2024-01-15T11:30:00Z"
}
```

## File Management Endpoints

### POST /api/contracts/{contractId}/files

Upload a file to a contract.

**Path Parameters:**
- `contractId` (int): Contract ID

**Request Body (multipart/form-data):**
- `file`: File to upload
- `folderType`: "Contract" or "AMC"

**Response (201 Created):**
```json
{
  "id": 2,
  "fileName": "new-contract-document.pdf",
  "filePath": "/contracts/1/new-contract-document.pdf",
  "fileSize": 2048000,
  "contentType": "application/pdf",
  "folderType": "Contract",
  "uploadedAt": "2024-01-15T12:00:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/contracts/1/files \
  -H "Authorization: Bearer <jwt-token>" \
  -F "file=@contract.pdf" \
  -F "folderType=Contract"
```

### GET /api/files/{id}/download

Download a file by ID.

**Path Parameters:**
- `id` (int): File ID

**Response (200 OK):**
Returns the file content with appropriate headers.

### DELETE /api/files/{id}

Delete a file (Admin or file owner only).

**Response (204 No Content)**

## AI Extraction Endpoints

### POST /api/contracts/{contractId}/extract/metadata

Extract metadata from contract using AI.

**Path Parameters:**
- `contractId` (int): Contract ID

**Request Body:**
```json
{
  "fileId": 1,
  "forceReextraction": false
}
```

**Response (200 OK):**
```json
{
  "contractId": 1,
  "extractedFields": [
    {
      "key": "ProjectName",
      "value": "Regional Transportation Hub Development",
      "confidence": 0.95,
      "source": "AI"
    },
    {
      "key": "ContractValue",
      "value": "45750000",
      "confidence": 0.99,
      "source": "AI"
    }
  ],
  "processingTime": 45.2,
  "overallConfidence": 0.93
}
```

### PUT /api/contracts/{contractId}/metadata/{fieldId}

Update a metadata field (human correction).

**Path Parameters:**
- `contractId` (int): Contract ID
- `fieldId` (int): Metadata field ID

**Request Body:**
```json
{
  "value": "Corrected Value",
  "source": "Human"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "key": "ProjectName",
  "value": "Corrected Value",
  "source": "Human",
  "confidence": 1.0,
  "updatedAt": "2024-01-15T13:00:00Z"
}
```

### POST /api/contracts/{contractId}/extract/obligations

Extract obligations from contract using AI.

**Response (200 OK):**
```json
{
  "contractId": 1,
  "extractedObligations": [
    {
      "description": "Submit comprehensive monthly progress reports...",
      "frequency": "Monthly",
      "dueDate": "2024-02-05",
      "penaltyText": "$10,000 for each day late",
      "confidence": 0.92,
      "source": "AI"
    }
  ],
  "processingTime": 67.8,
  "coverageRate": 0.857,
  "averageConfidence": 0.91
}
```

## Assignment Management Endpoints

### GET /api/assignments

Get assignments for the current user.

**Query Parameters:**
- `status` (string): Filter by status (Open, InProgress, Done, Overdue, Closed)
- `projectId` (int): Filter by project ID
- `dueDate` (date): Filter by due date

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "obligationId": 1,
      "obligationDescription": "Submit comprehensive monthly progress reports...",
      "assigneeUserId": 4,
      "assigneeName": "Ahmed Al-Rashid",
      "status": "InProgress",
      "percentComplete": 25,
      "dueDate": "2024-02-05",
      "contractTitle": "Transportation Hub Infrastructure",
      "projectName": "Project Alpha 202401151030",
      "evidenceCount": 2
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 20
}
```

### POST /api/assignments

Create a new assignment (Manager only).

**Request Body:**
```json
{
  "obligationId": 1,
  "assigneeUserId": 4,
  "dueDate": "2024-02-05",
  "notes": "Please prioritize this assignment due to project timeline."
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "obligationId": 1,
  "assigneeUserId": 4,
  "status": "Open",
  "percentComplete": 0,
  "createdAt": "2024-01-15T14:00:00Z"
}
```

### PUT /api/assignments/{id}/progress

Update assignment progress (Assignee only).

**Path Parameters:**
- `id` (int): Assignment ID

**Request Body:**
```json
{
  "percentComplete": 75,
  "status": "InProgress",
  "notes": "Completed most requirements, finalizing documentation."
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "InProgress",
  "percentComplete": 75,
  "updatedAt": "2024-01-15T15:00:00Z"
}
```

## Evidence Management Endpoints

### POST /api/assignments/{assignmentId}/evidence

Upload evidence for an assignment.

**Path Parameters:**
- `assignmentId` (int): Assignment ID

**Request Body (multipart/form-data):**
- `file`: Evidence file
- `description`: Description of the evidence

**Response (201 Created):**
```json
{
  "id": 3,
  "assignmentId": 1,
  "fileName": "progress-report-january.pdf",
  "filePath": "/evidence/1/progress-report-january.pdf",
  "fileSize": 512000,
  "contentType": "application/pdf",
  "description": "January progress report with photos and metrics",
  "uploadedAt": "2024-01-15T16:00:00Z"
}
```

### GET /api/assignments/{assignmentId}/evidence

Get all evidence for an assignment.

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "fileName": "monthly-progress-report-march-2024.pdf",
      "fileSize": 245760,
      "contentType": "application/pdf",
      "description": "Monthly progress report for March 2024",
      "uploadedAt": "2024-01-15T10:30:00Z"
    }
  ],
  "totalCount": 1
}
```

## Dashboard and Analytics Endpoints

### GET /api/dashboard/overview

Get dashboard overview data based on user role.

**Query Parameters:**
- `projectId` (int): Filter by project (optional)
- `dateFrom` (date): Start date for metrics
- `dateTo` (date): End date for metrics

**Response (200 OK):**
```json
{
  "summary": {
    "totalProjects": 2,
    "activeContracts": 2,
    "totalObligations": 18,
    "overdue Assignments": 1,
    "completedAssignments": 3,
    "totalPenaltyRisk": 75000.00
  },
  "recentActivity": [
    {
      "type": "AssignmentCompleted",
      "message": "Ahmed Al-Rashid completed monthly progress report",
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ],
  "upcomingDeadlines": [
    {
      "assignmentId": 2,
      "obligationDescription": "Weekly safety inspections...",
      "assigneeName": "Maria Gonzalez",
      "dueDate": "2024-01-17T00:00:00Z",
      "daysUntilDue": 2
    }
  ],
  "penaltyRisks": [
    {
      "obligationId": 3,
      "description": "Environmental monitoring report",
      "riskLevel": "High",
      "potentialPenalty": 15000.00,
      "daysOverdue": 1
    }
  ]
}
```

### GET /api/dashboard/metrics

Get detailed metrics for charts and reports.

**Query Parameters:**
- `projectId` (int): Filter by project
- `period` (string): "week", "month", "quarter", "year"
- `metricType` (string): "completion", "penalties", "compliance"

**Response (200 OK):**
```json
{
  "period": "month",
  "metricType": "completion",
  "data": [
    {
      "date": "2024-01-01",
      "value": 65.5,
      "label": "Completion Rate %"
    },
    {
      "date": "2024-01-08",
      "value": 72.3,
      "label": "Completion Rate %"
    }
  ],
  "summary": {
    "average": 68.9,
    "trend": "increasing",
    "changePercent": 10.4
  }
}
```

## AI Q&A Endpoints

### POST /api/ai/query

Ask natural language questions about contracts and obligations.

**Request Body:**
```json
{
  "question": "What are the obligations due this month for Project Alpha?",
  "projectIds": [1],
  "contractIds": [],
  "filters": {
    "status": "Active",
    "dateRange": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "answer": "For Project Alpha, there are 3 obligations due this month: 1) Monthly progress reports due January 5th, 2) Safety training certification due January 15th, 3) Insurance certificate renewal due January 30th.",
  "sources": [
    {
      "type": "Obligation",
      "id": 1,
      "title": "Monthly Progress Reports",
      "contractTitle": "Transportation Hub Infrastructure",
      "relevanceScore": 0.95
    }
  ],
  "confidence": 0.92,
  "processingTime": 2.3
}
```

### GET /api/ai/suggestions

Get AI-generated suggestions for queries.

**Query Parameters:**
- `projectId` (int): Context project ID
- `context` (string): Current user context

**Response (200 OK):**
```json
{
  "suggestions": [
    "Show me overdue obligations for active projects",
    "What penalties are we at risk for this quarter?",
    "List all evidence uploaded this week",
    "Compare obligation completion rates between projects"
  ]
}
```

## Notification Endpoints

### GET /api/notifications

Get notifications for the current user.

**Query Parameters:**
- `isRead` (bool): Filter by read status
- `type` (string): Filter by notification type
- `page` (int): Page number
- `pageSize` (int): Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "type": "AssignmentReminder",
      "title": "Reminder: Monthly Progress Reports Due Soon",
      "message": "Your monthly progress report is due in 5 days...",
      "isRead": false,
      "createdAt": "2024-01-15T08:00:00Z",
      "relatedEntityType": "Assignment",
      "relatedEntityId": 1
    }
  ],
  "unreadCount": 5,
  "totalCount": 12
}
```

### PUT /api/notifications/{id}/read

Mark a notification as read.

**Response (200 OK):**
```json
{
  "id": 1,
  "isRead": true,
  "readAt": "2024-01-15T17:00:00Z"
}
```

### PUT /api/notifications/mark-all-read

Mark all notifications as read for the current user.

**Response (200 OK):**
```json
{
  "message": "All notifications marked as read",
  "updatedCount": 5
}
```

## Search Endpoints

### GET /api/search

Global search across contracts, obligations, and metadata.

**Query Parameters:**
- `query` (string): Search terms
- `types` (array): Entity types to search ("Contracts", "Obligations", "Metadata")
- `projectIds` (array): Project IDs to filter by
- `page` (int): Page number
- `pageSize` (int): Items per page

**Response (200 OK):**
```json
{
  "results": [
    {
      "type": "Contract",
      "id": 1,
      "title": "Transportation Hub Infrastructure Development Contract",
      "excerpt": "...comprehensive monthly progress reports detailing construction advancement...",
      "score": 0.89,
      "projectName": "Project Alpha 202401151030"
    },
    {
      "type": "Obligation",
      "id": 1,
      "title": "Monthly Progress Reports",
      "excerpt": "Submit comprehensive monthly progress reports...",
      "score": 0.76,
      "contractTitle": "Transportation Hub Infrastructure"
    }
  ],
  "totalCount": 2,
  "searchTime": 0.045
}
```

## Error Handling

### Standard Error Response Format

```json
{
  "type": "ValidationError",
  "title": "Validation failed",
  "status": 400,
  "detail": "One or more validation errors occurred.",
  "errors": {
    "Email": ["Email is required"],
    "Password": ["Password must be at least 8 characters"]
  },
  "traceId": "00-trace-id-00"
}
```

### Common HTTP Status Codes

| Code | Description | Example |
|------|-------------|---------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Validation errors, malformed requests |
| 401 | Unauthorized | Invalid or missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource creation |
| 500 | Internal Server Error | Unexpected server errors |

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **File upload endpoints**: 10 requests per minute per user
- **AI extraction endpoints**: 20 requests per hour per user
- **General API endpoints**: 1000 requests per hour per user

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## API Versioning

The API uses URL path versioning:
- **Current version**: `/api/v1/...`
- **Future versions**: `/api/v2/...`

Version headers are also supported:
```
API-Version: 1.0
```

## Webhook Support (Future)

For real-time notifications, webhook endpoints will be available:

```json
{
  "webhookUrl": "https://your-app.com/webhooks/cip",
  "events": ["assignment.created", "assignment.overdue", "contract.uploaded"],
  "secret": "webhook-secret-key"
}
```

## SDK and Client Libraries

Official SDKs are planned for:
- JavaScript/TypeScript
- C#
- Python
- Mobile (React Native)

## Testing the API

### Postman Collection

A complete Postman collection is available at `/docs/postman/CIP-API.postman_collection.json` with:
- All endpoints with examples
- Environment variables for different deployments
- Automated tests for common scenarios
- Authentication token management

### Authentication Flow for Testing

1. **Login** with seed user credentials
2. **Copy the access token** from the response
3. **Add to Authorization header** for all subsequent requests
4. **Refresh token** when it expires (3600 seconds by default)

### Example Test Workflow

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin123!"}' \
  | jq -r '.accessToken')

# 2. Get projects
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/projects

# 3. Get contract details
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/contracts/1

# 4. Get user assignments
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/assignments
```

This API documentation provides comprehensive coverage of all endpoints with practical examples for testing and integration.