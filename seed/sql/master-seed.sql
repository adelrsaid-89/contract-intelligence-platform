-- Master Seed Script
-- Executes all seed scripts in the correct order
-- Respects SEED_MODE configuration and handles dependencies
-- Single entry point for seeding the Contract Intelligence Platform

PRINT '=======================================================';
PRINT 'Contract Intelligence Platform - Master Seed Script';
PRINT '=======================================================';
PRINT 'Starting seed data generation...';
PRINT 'Timestamp: ' + FORMAT(GETUTCDATE(), 'yyyy-MM-dd HH:mm:ss UTC');
PRINT '';

-- Check if database is ready
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
BEGIN
    PRINT 'ERROR: Database schema not found. Please run migrations first.';
    PRINT 'Expected tables: Users, Projects, Contracts, Obligations, Assignments, etc.';
    RETURN;
END;

PRINT 'Database schema validated successfully.';
PRINT '';

-- Execute seed scripts in dependency order
PRINT '1. Setting up seed configuration...';
:r seed-config.sql
PRINT '';

-- Check seed mode before proceeding
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'SEED_MODE is set to "none" - No seed data will be generated.';
    PRINT 'To generate sample data, update SeedConfiguration table:';
    PRINT 'UPDATE SeedConfiguration SET ConfigValue = ''example'' WHERE ConfigKey = ''SEED_MODE''';
    PRINT '';
    PRINT 'Current configuration:';
    SELECT ConfigKey, ConfigValue, Description FROM SeedConfiguration ORDER BY ConfigKey;
    RETURN;
END;

PRINT 'SEED_MODE: ' + dbo.GetSeedConfig('SEED_MODE');
PRINT 'Proceeding with seed data generation...';
PRINT '';

BEGIN TRY
    -- Start transaction for data consistency
    BEGIN TRANSACTION SeedData;

    PRINT '2. Creating users and roles...';
    :r 01-seed-users.sql
    PRINT '';

    PRINT '3. Creating projects...';
    :r 02-seed-projects.sql
    PRINT '';

    PRINT '4. Setting up user project permissions...';
    :r 03-seed-permissions.sql
    PRINT '';

    PRINT '5. Creating contracts and files...';
    :r 04-seed-contracts.sql
    PRINT '';

    PRINT '6. Generating contract metadata...';
    :r 05-seed-metadata.sql
    PRINT '';

    PRINT '7. Extracting obligations...';
    :r 06-seed-obligations.sql
    PRINT '';

    PRINT '8. Creating assignments...';
    :r 07-seed-assignments.sql
    PRINT '';

    PRINT '9. Uploading evidence files...';
    :r 08-seed-evidence.sql
    PRINT '';

    PRINT '10. Generating notifications...';
    :r 09-seed-notifications.sql
    PRINT '';

    -- Commit the transaction
    COMMIT TRANSACTION SeedData;

    PRINT '';
    PRINT '=======================================================';
    PRINT 'SEED DATA GENERATION COMPLETED SUCCESSFULLY!';
    PRINT '=======================================================';

    -- Generate summary report
    PRINT '';
    PRINT 'SUMMARY REPORT:';
    PRINT '---------------';

    DECLARE @userCount INT = (SELECT COUNT(*) FROM Users WHERE Email LIKE '%' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN'));
    DECLARE @projectCount INT = (SELECT COUNT(*) FROM Projects WHERE Name LIKE dbo.GetSeedConfig('PROJECT_PREFIX') + '%');
    DECLARE @contractCount INT = (SELECT COUNT(*) FROM Contracts WHERE ProjectId IN (SELECT CAST(ConfigValue AS INT) FROM SeedConfiguration WHERE ConfigKey IN ('PROJECT_1_ID', 'PROJECT_2_ID')));
    DECLARE @obligationCount INT = (SELECT COUNT(*) FROM Obligations WHERE ContractId IN (SELECT CAST(ConfigValue AS INT) FROM SeedConfiguration WHERE ConfigKey IN ('CONTRACT_1_ID', 'CONTRACT_2_ID')));
    DECLARE @assignmentCount INT = (SELECT COUNT(*) FROM Assignments a INNER JOIN Obligations o ON a.ObligationId = o.Id WHERE o.ContractId IN (SELECT CAST(ConfigValue AS INT) FROM SeedConfiguration WHERE ConfigKey IN ('CONTRACT_1_ID', 'CONTRACT_2_ID')));
    DECLARE @evidenceCount INT = (SELECT COUNT(*) FROM Evidence e INNER JOIN Assignments a ON e.AssignmentId = a.Id INNER JOIN Obligations o ON a.ObligationId = o.Id WHERE o.ContractId IN (SELECT CAST(ConfigValue AS INT) FROM SeedConfiguration WHERE ConfigKey IN ('CONTRACT_1_ID', 'CONTRACT_2_ID')));
    DECLARE @notificationCount INT = (SELECT COUNT(*) FROM Notifications WHERE UserId IN (SELECT CAST(ConfigValue AS INT) FROM SeedConfiguration WHERE ConfigKey LIKE '%_USER_ID'));

    PRINT 'Users Created: ' + CAST(@userCount AS NVARCHAR(10));
    PRINT 'Projects Created: ' + CAST(@projectCount AS NVARCHAR(10));
    PRINT 'Contracts Created: ' + CAST(@contractCount AS NVARCHAR(10));
    PRINT 'Obligations Extracted: ' + CAST(@obligationCount AS NVARCHAR(10));
    PRINT 'Assignments Created: ' + CAST(@assignmentCount AS NVARCHAR(10));
    PRINT 'Evidence Files: ' + CAST(@evidenceCount AS NVARCHAR(10));
    PRINT 'Notifications Generated: ' + CAST(@notificationCount AS NVARCHAR(10));

    PRINT '';
    PRINT 'DEFAULT CREDENTIALS:';
    PRINT '-------------------';
    PRINT 'Admin: admin@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('ADMIN_DEFAULT_PASSWORD');
    PRINT 'Manager 1: sarah.johnson@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('MANAGER_DEFAULT_PASSWORD');
    PRINT 'Manager 2: michael.chen@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('MANAGER_DEFAULT_PASSWORD');
    PRINT 'Subcontractor 1: ahmed.rashid@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('USER_DEFAULT_PASSWORD');
    PRINT 'Subcontractor 2: maria.gonzalez@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('USER_DEFAULT_PASSWORD');
    PRINT 'Subcontractor 3: david.smith@' + dbo.GetSeedConfig('USER_EMAIL_DOMAIN') + ' / ' + dbo.GetSeedConfig('USER_DEFAULT_PASSWORD');

    PRINT '';
    PRINT 'SAMPLE PROJECTS:';
    PRINT '---------------';
    PRINT '1. ' + dbo.GetSeedConfig('PROJECT_1_NAME') + ' (Transportation Hub)';
    PRINT '2. ' + dbo.GetSeedConfig('PROJECT_2_NAME') + ' (Commercial Mall)';

    PRINT '';
    PRINT 'KEY FEATURES DEMONSTRATED:';
    PRINT '-------------------------';
    PRINT '✓ Dynamic project and user management (no hardcoded names)';
    PRINT '✓ Role-based access control (RBAC) implementation';
    PRINT '✓ AI metadata extraction simulation (90%+ accuracy)';
    PRINT '✓ Obligation extraction with various frequencies';
    PRINT '✓ Assignment workflow with progress tracking';
    PRINT '✓ Evidence upload and management';
    PRINT '✓ Notification system for reminders and alerts';
    PRINT '✓ Penalty risk management and tracking';
    PRINT '✓ Multi-contract and multi-user scenarios';

    PRINT '';
    PRINT 'NEXT STEPS:';
    PRINT '----------';
    PRINT '1. Start the application backend and frontend';
    PRINT '2. Login with any of the provided credentials';
    PRINT '3. Explore dashboards specific to each user role';
    PRINT '4. Test AI Q&A system with sample questions';
    PRINT '5. Upload evidence files and track progress';
    PRINT '6. Review penalty risk analytics and reports';

    PRINT '';
    PRINT 'Configuration can be modified in the SeedConfiguration table.';
    PRINT 'To reset seed data, delete records and re-run this script.';
    PRINT '';
    PRINT 'Seed generation completed at: ' + FORMAT(GETUTCDATE(), 'yyyy-MM-dd HH:mm:ss UTC');

END TRY
BEGIN CATCH
    -- Rollback on error
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION SeedData;

    PRINT '';
    PRINT '=======================================================';
    PRINT 'ERROR DURING SEED DATA GENERATION';
    PRINT '=======================================================';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS NVARCHAR(10));
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS NVARCHAR(10));
    PRINT '';
    PRINT 'Transaction has been rolled back.';
    PRINT 'Please check the error and retry.';
    PRINT '';

    -- Re-throw the error
    THROW;
END CATCH;