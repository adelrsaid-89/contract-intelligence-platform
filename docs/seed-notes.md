# Seed Data Guide - Contract Intelligence Platform

This guide explains the seed data system, how to customize it, and how to use it effectively for testing and demonstration purposes.

## Overview

The seed data system provides a comprehensive set of sample data that demonstrates all aspects of the Contract Intelligence Platform. It's designed to be completely dynamic and configurable, with no hardcoded values.

## Seed Data Architecture

### Configuration-Driven Approach

The seed system uses a configuration table to manage all settings:

```sql
-- Core configuration options
SeedConfiguration (
    ConfigKey: Unique identifier for the setting
    ConfigValue: The actual value to use
    Description: Human-readable description
    CreatedAt/UpdatedAt: Audit timestamps
)
```

### Dynamic Data Generation

All data is generated dynamically using:
- Timestamps for uniqueness
- Configuration-driven naming
- Relationship preservation
- Realistic data patterns

## Seed Mode Configuration

### Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `none` | No seed data generated | Clean production environment |
| `example` | Full sample data with realistic content | Development, testing, demos |

### Switching Modes

```sql
-- Enable sample data
UPDATE SeedConfiguration
SET ConfigValue = 'example'
WHERE ConfigKey = 'SEED_MODE';

-- Disable seed data generation
UPDATE SeedConfiguration
SET ConfigValue = 'none'
WHERE ConfigKey = 'SEED_MODE';
```

## Generated Data Structure

### Users and Authentication

When `SEED_MODE = 'example'`, the following users are created:

```
Admin User:
- Email: admin@{domain}
- Password: Admin123!
- Role: Admin (0)
- Access: All projects and system functions

Manager Users:
- Email: sarah.johnson@{domain} | michael.chen@{domain}
- Password: Manager123!
- Role: Manager (1)
- Access: Assigned projects only

Subcontractor Users:
- Email: ahmed.rashid@{domain} | maria.gonzalez@{domain} | david.smith@{domain}
- Password: User123!
- Role: User (2)
- Access: Assigned obligations only
```

### Projects and Access Control

```
Project Structure:
- Project Alpha {timestamp}: Transportation Hub Development
  └── Manager: sarah.johnson@{domain}
  └── Contract: Transportation Hub Infrastructure ($45.75M)
      └── Obligations: 8 obligations with various frequencies
          └── Assignments: Distributed across subcontractors

- Project Beta {timestamp}: Metropolitan Shopping Center
  └── Manager: michael.chen@{domain}
  └── Contract: Commercial Retail Complex ($28.95M)
      └── Obligations: 10 obligations with various frequencies
          └── Assignments: Distributed across subcontractors
```

### Sample Contracts

Both contracts include:
- **Rich Metadata**: Project names, values, dates, clients, terms
- **Multiple Obligations**: Various frequencies (daily, weekly, monthly, quarterly)
- **Penalty Clauses**: Realistic penalty structures and amounts
- **KPIs and SLAs**: Measurable performance indicators
- **Realistic Content**: Professional contract language and structure

## Customization Options

### Basic Configuration

```sql
-- Change email domain for all users
UPDATE SeedConfiguration
SET ConfigValue = 'yourcompany.com'
WHERE ConfigKey = 'USER_EMAIL_DOMAIN';

-- Customize project naming
UPDATE SeedConfiguration
SET ConfigValue = 'YourProject'
WHERE ConfigKey = 'PROJECT_PREFIX';

-- Update file paths
UPDATE SeedConfiguration
SET ConfigValue = '/custom/path/contracts/'
WHERE ConfigKey = 'CONTRACT_FILE_PATH';
```

### Password Management

```sql
-- Update default passwords (remember to hash appropriately in production)
UPDATE SeedConfiguration
SET ConfigValue = 'NewAdminPass123!'
WHERE ConfigKey = 'ADMIN_DEFAULT_PASSWORD';

UPDATE SeedConfiguration
SET ConfigValue = 'NewManagerPass123!'
WHERE ConfigKey = 'MANAGER_DEFAULT_PASSWORD';

UPDATE SeedConfiguration
SET ConfigValue = 'NewUserPass123!'
WHERE ConfigKey = 'USER_DEFAULT_PASSWORD';
```

## Advanced Customization

### Adding Custom Users

```sql
-- Insert additional user
INSERT INTO Users (Name, Email, Role, PasswordHash, IsActive, CreatedAt, UpdatedAt)
VALUES (
    'Custom Manager',
    'custom.manager@yourcompany.com',
    1, -- Manager role
    HASHBYTES('SHA2_256', 'CustomPassword123!'),
    1,
    GETUTCDATE(),
    GETUTCDATE()
);

-- Grant project access
DECLARE @userId INT = SCOPE_IDENTITY();
DECLARE @projectId INT = CAST(dbo.GetSeedConfig('PROJECT_1_ID') AS INT);

INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel, GrantedAt)
VALUES (@userId, @projectId, 1, GETUTCDATE()); -- Manager access
```

### Creating Additional Projects

```sql
-- Create new project
INSERT INTO Projects (Name, Status, ClientName, Country, CreatedAt, UpdatedAt)
VALUES (
    'Custom Project Name',
    0, -- Active status
    'Custom Client',
    'Custom Country',
    GETUTCDATE(),
    GETUTCDATE()
);

-- Store project ID for reference
DECLARE @newProjectId INT = SCOPE_IDENTITY();
INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description)
VALUES ('CUSTOM_PROJECT_ID', CAST(@newProjectId AS NVARCHAR(10)), 'Custom project ID');
```

### Modifying Obligations

```sql
-- Add custom obligation to existing contract
DECLARE @contractId INT = CAST(dbo.GetSeedConfig('CONTRACT_1_ID') AS INT);
DECLARE @adminId INT = CAST(dbo.GetSeedConfig('ADMIN_USER_ID') AS INT);

INSERT INTO Obligations (
    ContractId,
    Description,
    Frequency,
    DueDate,
    PenaltyText,
    Source,
    Confidence,
    CreatedAt,
    UpdatedAt,
    CreatedBy,
    UpdatedBy
)
VALUES (
    @contractId,
    'Custom obligation description with specific requirements',
    'Custom frequency (e.g., Bi-monthly)',
    DATEADD(month, 2, GETDATE()),
    '$X,XXX penalty for non-compliance',
    1, -- Human source
    1.0, -- Full confidence
    GETUTCDATE(),
    GETUTCDATE(),
    @adminId,
    @adminId
);
```

## Data Relationships and Dependencies

### Execution Order

The seed scripts must be executed in this order to maintain referential integrity:

1. **seed-config.sql**: Base configuration setup
2. **01-seed-users.sql**: Users and authentication
3. **02-seed-projects.sql**: Projects and basic structure
4. **03-seed-permissions.sql**: User-project access relationships
5. **04-seed-contracts.sql**: Contracts and file references
6. **05-seed-metadata.sql**: AI-extracted metadata
6. **06-seed-obligations.sql**: Contract obligations
7. **07-seed-assignments.sql**: Obligation assignments to users
8. **08-seed-evidence.sql**: Evidence files and documentation
9. **09-seed-notifications.sql**: System notifications and alerts

### Dependency Graph

```
Users ──────┐
            ├─→ UserProjectPermissions
Projects ───┘

Projects ───→ Contracts ───→ MetadataFields
                      ├─→ Obligations ───→ Assignments ───→ Evidence
                      └─→ ContractFiles              └─→ Notifications

Users ──────────────────────────────────────────────────→ Assignments
                                                      └─→ Evidence
                                                      └─→ Notifications
```

## Testing Scenarios

### Role-Based Testing

Each seeded user type enables specific testing scenarios:

#### Admin Testing
```sql
-- Login as admin@{domain}
-- Expected capabilities:
- View all projects and contracts
- Access global dashboard with all metrics
- Manage users and permissions
- View system-wide penalty risks
- Access all audit logs
```

#### Manager Testing
```sql
-- Login as sarah.johnson@{domain} or michael.chen@{domain}
-- Expected capabilities:
- View only assigned projects
- Review and approve AI extractions
- Create and manage assignments
- Monitor team progress and penalties
- Receive overdue notifications
```

#### Subcontractor Testing
```sql
-- Login as ahmed.rashid@{domain}, maria.gonzalez@{domain}, or david.smith@{domain}
-- Expected capabilities:
- View only assigned obligations
- Update progress percentage
- Upload evidence files
- Receive assignment notifications
- Cannot access other users' data
```

### AI Extraction Testing

The seed data includes realistic AI extraction results:

```sql
-- View AI extraction results
SELECT
    c.Title as Contract,
    mf.Key as MetadataField,
    mf.Value,
    mf.Confidence,
    CASE mf.Source
        WHEN 0 THEN 'AI Extracted'
        WHEN 1 THEN 'Human Verified'
    END as Source
FROM MetadataFields mf
JOIN Contracts c ON mf.ContractId = c.Id
WHERE c.Id IN (
    CAST(dbo.GetSeedConfig('CONTRACT_1_ID') AS INT),
    CAST(dbo.GetSeedConfig('CONTRACT_2_ID') AS INT)
)
ORDER BY c.Title, mf.Key;
```

### Assignment Workflow Testing

```sql
-- View assignment distribution and progress
SELECT
    u.Name as Assignee,
    p.Name as Project,
    o.Description as Obligation,
    CASE a.Status
        WHEN 0 THEN 'Open'
        WHEN 1 THEN 'In Progress'
        WHEN 2 THEN 'Done'
        WHEN 3 THEN 'Overdue'
        WHEN 4 THEN 'Closed'
    END as Status,
    a.PercentComplete,
    o.DueDate,
    COUNT(e.Id) as EvidenceCount
FROM Assignments a
JOIN Users u ON a.AssigneeUserId = u.Id
JOIN Obligations o ON a.ObligationId = o.Id
JOIN Contracts c ON o.ContractId = c.Id
JOIN Projects p ON c.ProjectId = p.Id
LEFT JOIN Evidence e ON a.Id = e.AssignmentId
GROUP BY u.Name, p.Name, o.Description, a.Status, a.PercentComplete, o.DueDate
ORDER BY p.Name, u.Name, o.DueDate;
```

## Data Validation and Quality Assurance

### Validation Queries

```sql
-- Check data consistency
-- 1. Verify all users have proper project access
SELECT
    COUNT(DISTINCT u.Id) as TotalUsers,
    COUNT(DISTINCT upp.UserId) as UsersWithProjectAccess
FROM Users u
LEFT JOIN UserProjectPermissions upp ON u.Id = upp.UserId
WHERE u.Role IN (0, 1); -- Admin and Manager roles

-- 2. Verify all obligations have realistic due dates
SELECT
    COUNT(*) as TotalObligations,
    COUNT(CASE WHEN DueDate > GETDATE() THEN 1 END) as FutureObligations,
    COUNT(CASE WHEN DueDate <= GETDATE() THEN 1 END) as PastOrCurrentObligations
FROM Obligations;

-- 3. Check assignment distribution
SELECT
    u.Role,
    COUNT(a.Id) as AssignmentCount,
    AVG(CAST(a.PercentComplete AS FLOAT)) as AvgProgress
FROM Users u
LEFT JOIN Assignments a ON u.Id = a.AssigneeUserId
GROUP BY u.Role;
```

### Data Quality Metrics

The seed data is designed to achieve:
- **AI Extraction Accuracy**: 90%+ (simulated)
- **Obligation Coverage**: 85%+ of contract requirements
- **Assignment Distribution**: Balanced across subcontractors
- **Evidence Upload Rate**: 60%+ of in-progress assignments
- **Notification Delivery**: 100% for critical events

## Resetting and Regenerating Data

### Complete Reset

```sql
-- WARNING: This will delete ALL data
-- Back up any important data before running

-- Clear all seed data in reverse dependency order
DELETE FROM Notifications;
DELETE FROM Evidence;
DELETE FROM Assignments;
DELETE FROM PenaltyRisks;
DELETE FROM Obligations;
DELETE FROM MetadataFields;
DELETE FROM ContractFiles;
DELETE FROM Contracts;
DELETE FROM UserProjectPermissions;
DELETE FROM Projects;
DELETE FROM Users WHERE Email LIKE '%' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN');
DELETE FROM AuditLogs;

-- Clear configuration (optional)
DELETE FROM SeedConfiguration;

-- Re-run master seed script
:r master-seed.sql
```

### Partial Reset

```sql
-- Reset only assignments and evidence (keep users and contracts)
DELETE FROM Evidence;
DELETE FROM Assignments;

-- Re-run specific scripts
:r 07-seed-assignments.sql
:r 08-seed-evidence.sql
```

## Production Considerations

### Security

```sql
-- For production deployment:
-- 1. Change all default passwords
UPDATE SeedConfiguration
SET ConfigValue = 'SecureProductionPassword!'
WHERE ConfigKey LIKE '%_PASSWORD';

-- 2. Use proper password hashing
-- Implement bcrypt or similar in application layer

-- 3. Set SEED_MODE to 'none' for production
UPDATE SeedConfiguration
SET ConfigValue = 'none'
WHERE ConfigKey = 'SEED_MODE';
```

### Data Privacy

```sql
-- For GDPR/privacy compliance:
-- 1. Use generic, non-PII names and emails
-- 2. Implement data retention policies
-- 3. Add data anonymization scripts

-- Example anonymization
UPDATE Users
SET Name = 'User ' + CAST(Id AS NVARCHAR(10)),
    Email = 'user' + CAST(Id AS NVARCHAR(10)) + '@example.com'
WHERE Email LIKE '%' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN');
```

### Performance

```sql
-- For large-scale testing:
-- 1. Create additional projects and contracts
-- 2. Generate more realistic volumes of obligations
-- 3. Add historical data for trend analysis

-- Example: Generate 100 additional obligations
DECLARE @i INT = 1;
WHILE @i <= 100
BEGIN
    INSERT INTO Obligations (/* obligation data */)
    VALUES (/* dynamic values */);
    SET @i = @i + 1;
END;
```

## Troubleshooting Common Issues

### Issue: Seed Scripts Fail with Foreign Key Errors
**Solution**: Ensure scripts are run in the correct order and check for missing dependencies.

```sql
-- Check for missing references
SELECT 'Users' as TableName, COUNT(*) as Count FROM Users
UNION ALL
SELECT 'Projects', COUNT(*) FROM Projects
UNION ALL
SELECT 'UserProjectPermissions', COUNT(*) FROM UserProjectPermissions;
```

### Issue: Duplicate Data on Re-runs
**Solution**: Seed scripts include duplicate detection logic, but you can force clean state:

```sql
-- Check for existing data before seeding
IF EXISTS (SELECT 1 FROM Users WHERE Email LIKE '%@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN'))
BEGIN
    PRINT 'Seed data already exists. Use reset procedure if needed.';
    RETURN;
END;
```

### Issue: Configuration Not Taking Effect
**Solution**: Restart application or clear application cache after configuration changes.

```sql
-- Verify configuration changes
SELECT ConfigKey, ConfigValue, UpdatedAt
FROM SeedConfiguration
WHERE ConfigKey = 'TARGET_CONFIG_KEY';
```

This seed data system provides a robust foundation for testing, development, and demonstration of the Contract Intelligence Platform while maintaining flexibility and security best practices.