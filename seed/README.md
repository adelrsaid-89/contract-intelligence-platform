# Contract Intelligence Platform - Seed Data

This directory contains comprehensive seed data and sample files for the Contract Intelligence Platform POC.

## Directory Structure

```
seed/
├── contracts/          # Sample contract files
│   ├── sample-airport-contract.html
│   ├── sample-mall-contract.html
│   └── README.md
├── sql/               # Database seed scripts
│   ├── seed-config.sql
│   ├── 01-seed-users.sql
│   ├── 02-seed-projects.sql
│   ├── 03-seed-permissions.sql
│   ├── 04-seed-contracts.sql
│   ├── 05-seed-metadata.sql
│   ├── 06-seed-obligations.sql
│   ├── 07-seed-assignments.sql
│   ├── 08-seed-evidence.sql
│   ├── 09-seed-notifications.sql
│   └── master-seed.sql
├── evidence/          # Sample evidence files (created during runtime)
├── config/            # Configuration templates
└── README.md          # This file
```

## Quick Start

### 1. Database Seeding

Run the master seed script to populate the database with sample data:

```sql
-- SQL Server Management Studio or sqlcmd
:r master-seed.sql

-- Or execute individual scripts in order
:r seed-config.sql
:r 01-seed-users.sql
:r 02-seed-projects.sql
-- ... etc
```

### 2. Environment Configuration

The seed system supports two modes via the `SEED_MODE` configuration:

- **`example`**: Creates sample data with realistic content
- **`none`**: No seed data generated (empty system)

```sql
-- To change seed mode
UPDATE SeedConfiguration
SET ConfigValue = 'example'
WHERE ConfigKey = 'SEED_MODE';
```

### 3. Generated Sample Data

When `SEED_MODE=example`, the following data is created:

#### Users and Credentials
- **Admin**: admin@example.com / Admin123!
- **Manager 1**: sarah.johnson@example.com / Manager123!
- **Manager 2**: michael.chen@example.com / Manager123!
- **Subcontractor 1**: ahmed.rashid@example.com / User123!
- **Subcontractor 2**: maria.gonzalez@example.com / User123!
- **Subcontractor 3**: david.smith@example.com / User123!

#### Projects
- Transportation Hub Development (assigned to Manager 1)
- Commercial Shopping Center (assigned to Manager 2)

#### Contracts
- Transportation Hub Infrastructure Contract ($45.75M, 3 years)
- Commercial Retail Complex Contract ($28.95M, 2 years)

#### Sample Content
- 18 total obligations across both contracts
- Various frequencies: daily, weekly, bi-weekly, monthly, quarterly
- Realistic penalty clauses and KPIs
- Pre-assigned obligations to subcontractors
- Sample evidence files and notifications

## Configuration Options

All configuration is stored in the `SeedConfiguration` table and can be modified:

| ConfigKey | Default Value | Description |
|-----------|---------------|-------------|
| SEED_MODE | example | none or example |
| PROJECT_PREFIX | Project | Prefix for generated project names |
| USER_EMAIL_DOMAIN | example.com | Domain for user emails |
| CONTRACT_FILE_PATH | /seed/contracts/ | Path to contract files |
| ADMIN_DEFAULT_PASSWORD | Admin123! | Default admin password |
| MANAGER_DEFAULT_PASSWORD | Manager123! | Default manager password |
| USER_DEFAULT_PASSWORD | User123! | Default user password |

## Dynamic Data Features

The seed system is designed to be completely dynamic and non-hardcoded:

### 1. No Hardcoded Names
- Project names are generated with timestamps
- User names can be modified via configuration
- All relationships are maintained through IDs

### 2. Configurable Domains
- Email domains can be changed
- File paths are configurable
- Passwords can be updated

### 3. RBAC Enforcement
- Admin gets access to all projects
- Managers get access only to assigned projects
- Subcontractors see only assigned obligations

### 4. Realistic Data Relationships
- Contracts linked to projects
- Obligations extracted from contracts
- Assignments respect user permissions
- Evidence tied to specific assignments

## Testing Scenarios

The seed data enables testing of:

### 1. User Workflows
- **Admin**: Create projects, assign managers, view global dashboards
- **Manager**: Review AI extractions, assign obligations, track progress
- **Subcontractor**: Update progress, upload evidence, view assignments

### 2. AI Extraction Testing
- Metadata extraction with confidence scores
- Obligation identification with frequencies
- Penalty clause recognition
- Various document structures

### 3. Search and Q&A
- Cross-contract queries
- Project-filtered searches
- Obligation frequency analysis
- Penalty risk identification

### 4. Dashboard Analytics
- Progress tracking across roles
- Penalty risk visualization
- KPI compliance monitoring
- Evidence upload tracking

## Customization

### 1. Adding New Users
```sql
-- Add new user
INSERT INTO Users (Name, Email, Role, PasswordHash, IsActive)
VALUES ('New User', 'new.user@example.com', 2, 'hashed_password', 1);

-- Grant project access
INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel)
VALUES (@newUserId, @projectId, 2); -- Viewer access
```

### 2. Creating Additional Projects
```sql
-- Add new project
INSERT INTO Projects (Name, Status, ClientName, Country)
VALUES ('New Project', 0, 'New Client', 'Country');

-- Assign manager
INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel)
VALUES (@managerId, @newProjectId, 1); -- Manager access
```

### 3. Modifying Seed Configuration
```sql
-- Update configuration
UPDATE SeedConfiguration
SET ConfigValue = 'new_value'
WHERE ConfigKey = 'config_key';

-- Re-run specific seed scripts to apply changes
```

## Resetting Seed Data

To completely reset and regenerate seed data:

```sql
-- Clear all seed data (preserve schema)
DELETE FROM Notifications;
DELETE FROM Evidence;
DELETE FROM Assignments;
DELETE FROM Obligations;
DELETE FROM MetadataFields;
DELETE FROM ContractFiles;
DELETE FROM Contracts;
DELETE FROM UserProjectPermissions;
DELETE FROM Projects;
DELETE FROM Users;
DELETE FROM SeedConfiguration;

-- Re-run master seed script
:r master-seed.sql
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Ensure database schema exists before running seeds
   - Run migration scripts first

2. **Configuration Errors**
   - Check `SeedConfiguration` table for correct values
   - Verify SEED_MODE is set correctly

3. **Permission Issues**
   - Ensure proper SQL Server permissions
   - Check file path access for evidence uploads

4. **Duplicate Data**
   - Seed scripts check for existing data
   - Use reset procedure above to clean start

### Validation Queries

```sql
-- Check seed status
SELECT ConfigKey, ConfigValue FROM SeedConfiguration ORDER BY ConfigKey;

-- Verify user creation
SELECT Name, Email, Role FROM Users;

-- Check project assignments
SELECT u.Name, p.Name as Project, upp.AccessLevel
FROM UserProjectPermissions upp
JOIN Users u ON upp.UserId = u.Id
JOIN Projects p ON upp.ProjectId = p.Id;

-- Validate obligations and assignments
SELECT COUNT(*) as ObligationCount FROM Obligations;
SELECT COUNT(*) as AssignmentCount FROM Assignments;
SELECT COUNT(*) as EvidenceCount FROM Evidence;
```

## Integration with Application

The seed data is designed to work seamlessly with the application:

1. **Authentication**: Use provided credentials to log in
2. **File Paths**: Contract files should be accessible at configured paths
3. **Evidence Storage**: Evidence directory should be writable
4. **API Endpoints**: All entities created have proper relationships for API access

For questions or issues with seed data, refer to the main documentation or contact the development team.