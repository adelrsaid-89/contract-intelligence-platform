-- Seed Contracts Script
-- Creates sample contracts linked to projects and files
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping contract seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting contract seeding...';

-- Get project IDs from configuration
DECLARE @project1Id INT = CAST(dbo.GetSeedConfig('PROJECT_1_ID') AS INT);
DECLARE @project2Id INT = CAST(dbo.GetSeedConfig('PROJECT_2_ID') AS INT);
DECLARE @adminId INT = CAST(dbo.GetSeedConfig('ADMIN_USER_ID') AS INT);

-- Validate that we have the required IDs
IF @project1Id IS NULL OR @project2Id IS NULL OR @adminId IS NULL
BEGIN
    PRINT 'ERROR: Missing required project or user IDs from configuration. Please run previous seeding scripts first.';
    RETURN;
END;

-- Check if contracts already exist for these projects
IF NOT EXISTS (SELECT 1 FROM Contracts WHERE ProjectId IN (@project1Id, @project2Id))
BEGIN
    -- Create contracts
    INSERT INTO Contracts (ProjectId, Title, ContractValue, StartDate, EndDate, PaymentTerms, Status, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    (@project1Id, 'Transportation Hub Infrastructure Development Contract', 45750000.00, '2024-03-01', '2027-02-28', 'Monthly progress payments within 30 days of invoice', 1, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@project2Id, 'Commercial Retail Complex Development Contract', 28950000.00, '2024-06-15', '2026-05-30', 'Bi-weekly progress payments within 21 days of invoice', 1, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId);

    DECLARE @contract1Id INT = (SELECT Id FROM Contracts WHERE ProjectId = @project1Id AND Title LIKE 'Transportation Hub%');
    DECLARE @contract2Id INT = (SELECT Id FROM Contracts WHERE ProjectId = @project2Id AND Title LIKE 'Commercial Retail%');

    PRINT 'Created contracts:';
    PRINT '  Contract 1 ID: ' + CAST(@contract1Id AS NVARCHAR(10)) + ' for project ' + dbo.GetSeedConfig('PROJECT_1_NAME');
    PRINT '  Contract 2 ID: ' + CAST(@contract2Id AS NVARCHAR(10)) + ' for project ' + dbo.GetSeedConfig('PROJECT_2_NAME');

    -- Create contract files
    DECLARE @contractFilePath NVARCHAR(500) = dbo.GetSeedConfig('CONTRACT_FILE_PATH');

    INSERT INTO ContractFiles (ContractId, FileName, FilePath, FileSize, ContentType, FolderType, UploadedBy, UploadedAt)
    VALUES
    (@contract1Id, 'sample-airport-contract.pdf', @contractFilePath + 'sample-airport-contract.pdf', 1024000, 'application/pdf', 0, @adminId, GETUTCDATE()),
    (@contract2Id, 'sample-mall-contract.pdf', @contractFilePath + 'sample-mall-contract.pdf', 896000, 'application/pdf', 0, @adminId, GETUTCDATE());

    DECLARE @file1Id INT = (SELECT Id FROM ContractFiles WHERE ContractId = @contract1Id);
    DECLARE @file2Id INT = (SELECT Id FROM ContractFiles WHERE ContractId = @contract2Id);

    PRINT 'Created contract files:';
    PRINT '  File 1 ID: ' + CAST(@file1Id AS NVARCHAR(10));
    PRINT '  File 2 ID: ' + CAST(@file2Id AS NVARCHAR(10));

    -- Store contract and file IDs for use in other scripts
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('CONTRACT_1_ID', CAST(@contract1Id AS NVARCHAR(10)), 'ID of the first seeded contract'),
    ('CONTRACT_2_ID', CAST(@contract2Id AS NVARCHAR(10)), 'ID of the second seeded contract'),
    ('CONTRACT_FILE_1_ID', CAST(@file1Id AS NVARCHAR(10)), 'ID of the first contract file'),
    ('CONTRACT_FILE_2_ID', CAST(@file2Id AS NVARCHAR(10)), 'ID of the second contract file');

    PRINT 'Contract seeding completed successfully!';
END
ELSE
BEGIN
    PRINT 'Contracts already exist for these projects. Skipping contract creation.';

    -- Get existing contract IDs
    DECLARE @existingContract1Id INT = (SELECT TOP 1 Id FROM Contracts WHERE ProjectId = @project1Id ORDER BY Id);
    DECLARE @existingContract2Id INT = (SELECT TOP 1 Id FROM Contracts WHERE ProjectId = @project2Id ORDER BY Id);

    -- Update configuration with existing contract IDs
    MERGE SeedConfiguration AS target
    USING (VALUES
        ('CONTRACT_1_ID', CAST(@existingContract1Id AS NVARCHAR(10))),
        ('CONTRACT_2_ID', CAST(@existingContract2Id AS NVARCHAR(10)))
    ) AS source (ConfigKey, ConfigValue)
    ON target.ConfigKey = source.ConfigKey
    WHEN MATCHED THEN
        UPDATE SET ConfigValue = source.ConfigValue, UpdatedAt = GETUTCDATE()
    WHEN NOT MATCHED THEN
        INSERT (ConfigKey, ConfigValue, Description) VALUES (source.ConfigKey, source.ConfigValue, 'Existing contract information');
END;