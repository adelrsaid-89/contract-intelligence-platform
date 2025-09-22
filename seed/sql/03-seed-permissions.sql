-- Seed User Project Permissions Script
-- Creates project permissions for users based on their roles
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping permission seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting permission seeding...';

-- Get user and project IDs from configuration
DECLARE @adminId INT = CAST(dbo.GetSeedConfig('ADMIN_USER_ID') AS INT);
DECLARE @manager1Id INT = CAST(dbo.GetSeedConfig('MANAGER_1_USER_ID') AS INT);
DECLARE @manager2Id INT = CAST(dbo.GetSeedConfig('MANAGER_2_USER_ID') AS INT);
DECLARE @project1Id INT = CAST(dbo.GetSeedConfig('PROJECT_1_ID') AS INT);
DECLARE @project2Id INT = CAST(dbo.GetSeedConfig('PROJECT_2_ID') AS INT);

-- Validate that we have the required IDs
IF @adminId IS NULL OR @manager1Id IS NULL OR @manager2Id IS NULL OR @project1Id IS NULL OR @project2Id IS NULL
BEGIN
    PRINT 'ERROR: Missing required user or project IDs from configuration. Please run user and project seeding first.';
    RETURN;
END;

-- Check if permissions already exist
IF NOT EXISTS (SELECT 1 FROM UserProjectPermissions WHERE UserId = @adminId)
BEGIN
    -- Admin gets Owner access to all projects
    INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel, GrantedAt)
    VALUES
    (@adminId, @project1Id, 0, GETUTCDATE()), -- Owner access
    (@adminId, @project2Id, 0, GETUTCDATE()); -- Owner access

    PRINT 'Granted Admin user Owner access to all projects';

    -- Manager 1 gets Manager access to Project 1
    INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel, GrantedAt)
    VALUES
    (@manager1Id, @project1Id, 1, GETUTCDATE()); -- Manager access

    PRINT 'Granted Manager 1 access to Project 1';

    -- Manager 2 gets Manager access to Project 2
    INSERT INTO UserProjectPermissions (UserId, ProjectId, AccessLevel, GrantedAt)
    VALUES
    (@manager2Id, @project2Id, 1, GETUTCDATE()); -- Manager access

    PRINT 'Granted Manager 2 access to Project 2';

    -- Note: Subcontractors get access through assignments, not direct project permissions
    -- This follows the RBAC model where subcontractors only see assigned obligations

    PRINT 'Permission seeding completed successfully!';

    -- Summary
    PRINT 'Permission Summary:';
    PRINT '  Admin: Owner access to all projects';
    PRINT '  Manager 1: Manager access to ' + dbo.GetSeedConfig('PROJECT_1_NAME');
    PRINT '  Manager 2: Manager access to ' + dbo.GetSeedConfig('PROJECT_2_NAME');
    PRINT '  Subcontractors: Access granted through specific obligation assignments';
END
ELSE
BEGIN
    PRINT 'Permissions already exist. Skipping permission creation.';

    -- Display current permissions for reference
    SELECT
        u.Name as UserName,
        u.Email,
        p.Name as ProjectName,
        CASE upp.AccessLevel
            WHEN 0 THEN 'Owner'
            WHEN 1 THEN 'Manager'
            WHEN 2 THEN 'Viewer'
        END as AccessLevel,
        upp.GrantedAt
    FROM UserProjectPermissions upp
    INNER JOIN Users u ON upp.UserId = u.Id
    INNER JOIN Projects p ON upp.ProjectId = p.Id
    ORDER BY u.Role, u.Name, p.Name;
END;