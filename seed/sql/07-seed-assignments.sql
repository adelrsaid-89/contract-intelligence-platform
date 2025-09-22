-- Seed Assignments Script
-- Creates sample assignments of obligations to subcontractors
-- Demonstrates the RBAC model where subcontractors only see assigned tasks
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping assignment seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting assignment seeding...';

-- Get user and obligation IDs from configuration
DECLARE @subcontractor1Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_1_USER_ID') AS INT);
DECLARE @subcontractor2Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_2_USER_ID') AS INT);
DECLARE @subcontractor3Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_3_USER_ID') AS INT);
DECLARE @contract1Id INT = CAST(dbo.GetSeedConfig('CONTRACT_1_ID') AS INT);
DECLARE @contract2Id INT = CAST(dbo.GetSeedConfig('CONTRACT_2_ID') AS INT);
DECLARE @manager1Id INT = CAST(dbo.GetSeedConfig('MANAGER_1_USER_ID') AS INT);
DECLARE @manager2Id INT = CAST(dbo.GetSeedConfig('MANAGER_2_USER_ID') AS INT);

-- Validate that we have the required IDs
IF @subcontractor1Id IS NULL OR @subcontractor2Id IS NULL OR @subcontractor3Id IS NULL OR @contract1Id IS NULL OR @contract2Id IS NULL
BEGIN
    PRINT 'ERROR: Missing required user or contract IDs from configuration. Please run previous seeding scripts first.';
    RETURN;
END;

-- Get some obligations to assign
DECLARE @obligation1Id INT, @obligation2Id INT, @obligation3Id INT, @obligation4Id INT, @obligation5Id INT;
DECLARE @obligation6Id INT, @obligation7Id INT, @obligation8Id INT, @obligation9Id INT, @obligation10Id INT;

-- Get obligations from Contract 1 (Transportation Hub)
SELECT TOP 5
    @obligation1Id = MIN(CASE WHEN rn = 1 THEN Id END),
    @obligation2Id = MIN(CASE WHEN rn = 2 THEN Id END),
    @obligation3Id = MIN(CASE WHEN rn = 3 THEN Id END),
    @obligation4Id = MIN(CASE WHEN rn = 4 THEN Id END),
    @obligation5Id = MIN(CASE WHEN rn = 5 THEN Id END)
FROM (
    SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn
    FROM Obligations
    WHERE ContractId = @contract1Id
) ranked;

-- Get obligations from Contract 2 (Commercial Mall)
SELECT TOP 5
    @obligation6Id = MIN(CASE WHEN rn = 1 THEN Id END),
    @obligation7Id = MIN(CASE WHEN rn = 2 THEN Id END),
    @obligation8Id = MIN(CASE WHEN rn = 3 THEN Id END),
    @obligation9Id = MIN(CASE WHEN rn = 4 THEN Id END),
    @obligation10Id = MIN(CASE WHEN rn = 5 THEN Id END)
FROM (
    SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn
    FROM Obligations
    WHERE ContractId = @contract2Id
) ranked;

-- Check if assignments already exist
IF NOT EXISTS (SELECT 1 FROM Assignments WHERE ObligationId IN (@obligation1Id, @obligation2Id, @obligation3Id, @obligation4Id, @obligation5Id, @obligation6Id, @obligation7Id, @obligation8Id, @obligation9Id, @obligation10Id))
BEGIN
    -- Create assignments for Contract 1 obligations
    INSERT INTO Assignments (ObligationId, AssigneeUserId, Status, PercentComplete, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- Subcontractor 1 (Ahmed) - Multiple assignments with different progress levels
    (@obligation1Id, @subcontractor1Id, 1, 25, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id), -- In Progress - Monthly reports
    (@obligation3Id, @subcontractor1Id, 0, 0, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id),   -- Open - Safety training

    -- Subcontractor 2 (Maria) - Different obligations and progress
    (@obligation2Id, @subcontractor2Id, 2, 100, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id), -- Done - Subcontractor reports
    (@obligation4Id, @subcontractor2Id, 1, 60, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id),  -- In Progress - Insurance maintenance

    -- Subcontractor 3 (David) - Mixed progress
    (@obligation5Id, @subcontractor3Id, 1, 40, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id),  -- In Progress - Environmental monitoring
    (@obligation7Id, @subcontractor3Id, 0, 0, GETUTCDATE(), GETUTCDATE(), @manager1Id, @manager1Id);   -- Open - System integration

    -- Create assignments for Contract 2 obligations
    INSERT INTO Assignments (ObligationId, AssigneeUserId, Status, PercentComplete, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- Distribute Contract 2 obligations across subcontractors
    (@obligation6Id, @subcontractor1Id, 1, 50, GETUTCDATE(), GETUTCDATE(), @manager2Id, @manager2Id),  -- In Progress - Bi-weekly reports
    (@obligation8Id, @subcontractor1Id, 0, 0, GETUTCDATE(), GETUTCDATE(), @manager2Id, @manager2Id),   -- Open - Quality audits

    (@obligation9Id, @subcontractor2Id, 1, 75, GETUTCDATE(), GETUTCDATE(), @manager2Id, @manager2Id),  -- In Progress - Emergency drills
    (@obligation10Id, @subcontractor2Id, 2, 100, GETUTCDATE(), GETUTCDATE(), @manager2Id, @manager2Id), -- Done - Daily environmental monitoring

    -- Some obligations showing overdue status (simulate T-14 day reminders)
    (@obligation7Id, @subcontractor3Id, 3, 30, GETUTCDATE(), GETUTCDATE(), @manager2Id, @manager2Id);   -- Overdue - Safety inspections

    PRINT 'Assignment seeding completed successfully!';

    -- Display assignment summary
    SELECT
        u.Name as AssigneeName,
        u.Email,
        c.Title as ContractTitle,
        o.Description as ObligationDescription,
        CASE a.Status
            WHEN 0 THEN 'Open'
            WHEN 1 THEN 'In Progress'
            WHEN 2 THEN 'Done'
            WHEN 3 THEN 'Overdue'
            WHEN 4 THEN 'Closed'
        END as Status,
        a.PercentComplete,
        FORMAT(o.DueDate, 'yyyy-MM-dd') as DueDate
    FROM Assignments a
    INNER JOIN Users u ON a.AssigneeUserId = u.Id
    INNER JOIN Obligations o ON a.ObligationId = o.Id
    INNER JOIN Contracts c ON o.ContractId = c.Id
    WHERE o.ContractId IN (@contract1Id, @contract2Id)
    ORDER BY u.Name, c.Title, a.Status;

    -- Display statistics
    PRINT '';
    PRINT 'Assignment Statistics:';
    PRINT 'Total Assignments Created: ' + CAST(@@ROWCOUNT AS NVARCHAR(10));

    SELECT
        CASE Status
            WHEN 0 THEN 'Open'
            WHEN 1 THEN 'In Progress'
            WHEN 2 THEN 'Done'
            WHEN 3 THEN 'Overdue'
            WHEN 4 THEN 'Closed'
        END as Status,
        COUNT(*) as Count,
        AVG(CAST(PercentComplete AS FLOAT)) as AvgProgress
    FROM Assignments a
    INNER JOIN Obligations o ON a.ObligationId = o.Id
    WHERE o.ContractId IN (@contract1Id, @contract2Id)
    GROUP BY Status
    ORDER BY Status;

    -- Store assignment information for use in notifications/evidence seeding
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('SAMPLE_ASSIGNMENT_COUNT', CAST(@@ROWCOUNT AS NVARCHAR(10)), 'Number of sample assignments created'),
    ('ASSIGNMENTS_CREATED', 'true', 'Flag indicating assignments have been seeded');

    PRINT 'Assignments demonstrate RBAC model:';
    PRINT '- Subcontractors will only see their assigned obligations';
    PRINT '- Managers see assignments they created for their projects';
    PRINT '- Admin sees all assignments across all projects';
    PRINT '- Some assignments show different progress levels for testing';
    PRINT '- One assignment marked as overdue for penalty risk testing';
END
ELSE
BEGIN
    PRINT 'Assignments already exist for these obligations. Skipping assignment creation.';

    -- Display existing assignments summary
    SELECT
        u.Name as AssigneeName,
        CASE a.Status
            WHEN 0 THEN 'Open'
            WHEN 1 THEN 'In Progress'
            WHEN 2 THEN 'Done'
            WHEN 3 THEN 'Overdue'
            WHEN 4 THEN 'Closed'
        END as Status,
        COUNT(*) as Count,
        AVG(CAST(a.PercentComplete AS FLOAT)) as AvgProgress
    FROM Assignments a
    INNER JOIN Users u ON a.AssigneeUserId = u.Id
    INNER JOIN Obligations o ON a.ObligationId = o.Id
    WHERE o.ContractId IN (@contract1Id, @contract2Id)
    GROUP BY u.Name, a.Status
    ORDER BY u.Name, a.Status;
END;