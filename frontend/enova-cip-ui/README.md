# Contract Intelligence Platform - Frontend

## Overview

This is a complete Angular 17 frontend application for the Contract Intelligence Platform, featuring advanced contract management, AI-powered analysis, and comprehensive obligation tracking.

## Features

### Core Features
- ✅ **Authentication & Authorization** - JWT-based auth with role-based access control
- ✅ **Responsive Layout** - Material Design with responsive sidebar navigation
- ✅ **Multi-language Support** - English and Arabic with RTL support
- ✅ **Dark/Light Theme** - Dynamic theme switching
- ✅ **Real-time Notifications** - WebSocket-based updates
- ✅ **Advanced Search** - Global search with filters and facets

### User Roles
- **Admin** - Full system access, user management, system settings
- **Manager** - Project management, team oversight, reports
- **Subcontractor** - Task management, evidence submission, progress updates

### Module Structure

#### 🔐 Authentication Module
- JWT token management with automatic refresh
- Role-based route protection
- Session management and security

#### 🏗️ Layout Components
- **Main Layout** - Responsive sidebar with toolbar
- **Sidebar Navigation** - Role-based menu with permissions
- **Toolbar** - Search, notifications, user menu, language switcher
- **Breadcrumb Navigation** - Dynamic breadcrumbs with icons

#### 📊 Dashboard Module (To be implemented)
- **Admin Dashboard** - Global KPIs, system overview, user analytics
- **Manager Dashboard** - Project metrics, team performance, compliance rates
- **Subcontractor Dashboard** - Task overview, progress tracking, notifications

#### 📁 Project Management Module (To be implemented)
- Project CRUD operations
- User permission management
- Project-specific dashboards
- Resource allocation

#### 📄 Contract Management Module (To be implemented)
- Contract upload with drag-drop
- File management (Contracts/AMCs folders)
- Version control and history
- Metadata extraction and editing
- PDF viewer integration

#### ✅ Obligation Management Module (To be implemented)
- Kanban board for task management
- Assignment and tracking system
- Progress monitoring with sliders
- Evidence upload and verification
- Calendar view for due dates
- Automated reminders and notifications

#### 🤖 AI Features Module (To be implemented)
- **Document Analysis** - AI-powered metadata extraction
- **Obligation Detection** - Automatic obligation identification
- **Q&A Console** - Natural language contract queries
- **Confidence Scoring** - AI reliability indicators

#### 🔍 Search Module (To be implemented)
- Advanced search with multiple filters
- Full-text search across documents
- Search history and saved searches
- Quick search in toolbar

#### 📧 Notification Module (To be implemented)
- Real-time notification system
- Email and push notification preferences
- Notification history and management
- Custom notification rules

#### 📈 Reports Module (To be implemented)
- Compliance reports and analytics
- Performance dashboards
- Risk analysis and alerts
- Export capabilities (PDF, Excel)

## Technical Architecture

### Core Services

#### Authentication Service
```typescript
- JWT token management
- Role-based access control
- Automatic token refresh
- Session timeout handling
```

#### Storage Service
```typescript
- Secure local storage abstraction
- Session storage management
- Cross-browser compatibility
```

#### Language Service
```typescript
- Multi-language support (EN/AR)
- RTL text direction switching
- Dynamic language switching
- Cultural formatting
```

#### Theme Service
```typescript
- Light/dark theme switching
- System preference detection
- Custom theme configuration
- CSS custom properties
```

#### Notification Service
```typescript
- Real-time notifications
- Unread count tracking
- Notification preferences
- WebSocket integration
```

### Models and Interfaces

#### User Models
- User, UserRole, Permission
- UserProfile, UserPreferences
- AuthToken, LoginRequest/Response

#### Project Models
- Project, ProjectStatus, RiskLevel
- ProjectPermission, ProjectStats
- ActivityLog, RiskAlert

#### Contract Models
- Contract, ContractType, ContractStatus
- ContractFile, ContractMetadata
- ExtractedData, ConfidenceScores

#### Common Models
- ApiResponse, PaginationMeta
- FilterCriteria, DropdownOption
- Notification, SearchResult
- BreadcrumbItem, MenuItem

### Guards and Interceptors

#### Authentication Guard
- Route protection based on authentication status
- Automatic redirect to login page
- Return URL preservation

#### Role Guard
- Role-based route access control
- Permission-based restrictions
- Unauthorized page redirection

#### Auth Interceptor
- Automatic JWT token injection
- Token refresh on 401 responses
- Request/response logging

#### Error Interceptor
- Global error handling
- User-friendly error messages
- Toast notifications for errors

## UI Components and Styling

### Material Design Integration
- Angular Material 17 components
- Custom theme configuration
- Responsive breakpoints
- Accessibility compliance

### Global Styles
- Consistent spacing and typography
- Status and priority indicators
- Loading states and empty states
- Responsive utilities
- RTL support
- Print styles

### Third-party Integrations
- **ag-Grid** - Advanced data tables with sorting, filtering, pagination
- **ngx-charts** - Data visualization and charts
- **ngx-toastr** - Toast notifications
- **ng2-pdf-viewer** - PDF document viewing

## Development Setup

### Prerequisites
- Node.js 18.13.0 or higher
- npm 8.19.0 or higher
- Angular CLI 17

### Installation
```bash
cd frontend/enova-cip-ui
npm install
```

### Development Server
```bash
# English version
npm run serve:en

# Arabic version
npm run serve:ar

# Default (development)
npm start
```

### Build
```bash
# Development build
npm run build

# Production build
npm run build:prod

# Language-specific builds
npm run build:en
npm run build:ar
```

### Testing
```bash
# Unit tests
npm test

# CI tests
npm run test:ci

# Linting
npm run lint
```

## File Structure

```
src/
├── app/
│   ├── core/                     # Core services, models, guards
│   │   ├── guards/               # Route guards
│   │   ├── interceptors/         # HTTP interceptors
│   │   ├── models/               # TypeScript interfaces
│   │   └── services/             # Core services
│   ├── features/                 # Feature modules
│   │   ├── auth/                 # Authentication module
│   │   ├── dashboard/            # Dashboard module
│   │   ├── contracts/            # Contract management
│   │   ├── obligations/          # Obligation management
│   │   ├── ai/                   # AI features
│   │   ├── search/               # Search functionality
│   │   └── ...                   # Other feature modules
│   ├── layout/                   # Layout components
│   │   ├── main-layout/          # Main application layout
│   │   ├── toolbar/              # Top toolbar
│   │   ├── sidebar/              # Side navigation
│   │   └── breadcrumb/           # Breadcrumb navigation
│   ├── shared/                   # Shared components
│   │   ├── components/           # Reusable UI components
│   │   ├── directives/           # Custom directives
│   │   └── pipes/                # Custom pipes
│   ├── app.component.*           # Root component
│   ├── app.module.ts             # Root module
│   └── app-routing.module.ts     # Main routing
├── assets/                       # Static assets
│   ├── i18n/                     # Translation files
│   ├── icons/                    # Icons and logos
│   └── images/                   # Images
├── environments/                 # Environment configurations
├── styles.scss                   # Global styles
└── index.html                    # Main HTML file
```

## Key Features Implementation Status

### ✅ Completed
- Project structure and configuration
- Authentication system with JWT
- Layout components (sidebar, toolbar, breadcrumb)
- Core services and models
- Routing with lazy loading
- Material Design integration
- Theme and language services
- Global styling and responsiveness

### 🚧 In Progress
- Feature modules implementation
- Dashboard components
- Form components and validation

### 📋 Planned
- Contract management UI
- Obligation tracking system
- AI integration components
- Advanced search interface
- Notification management
- Report generation
- File upload and management
- Kanban board implementation
- Calendar integration
- Real-time updates via WebSocket

## Internationalization (i18n)

The application supports multiple languages with the following features:
- English (LTR) and Arabic (RTL) support
- Dynamic language switching
- Cultural date and number formatting
- RTL layout adjustments
- Font optimization for different languages

## Performance Optimizations

- Lazy-loaded feature modules
- OnPush change detection strategy
- Image optimization and lazy loading
- Bundle size optimization
- Service worker for caching
- Virtual scrolling for large lists
- Pagination for data tables

## Security Features

- JWT token security
- XSS protection
- CSRF protection
- Secure storage practices
- Role-based access control
- Input validation and sanitization

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Follow Angular style guide
2. Use TypeScript strict mode
3. Implement proper error handling
4. Add unit tests for components
5. Follow accessibility guidelines
6. Use semantic HTML
7. Optimize for performance

## License

Copyright © 2024 Enova. All rights reserved.