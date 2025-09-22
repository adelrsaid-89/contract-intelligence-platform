-- Seed Projects Script
-- Creates sample projects with dynamic names
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping project seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting project seeding...';

-- Variables for dynamic configuration
DECLARE @projectPrefix NVARCHAR(50) = dbo.GetSeedConfig('PROJECT_PREFIX');

-- Generate unique project names with timestamps to avoid conflicts
DECLARE @timestamp NVARCHAR(20) = FORMAT(GETUTCDATE(), 'yyyyMMddHHmm');
DECLARE @project1Name NVARCHAR(200) = @projectPrefix + ' Alpha ' + @timestamp;
DECLARE @project2Name NVARCHAR(200) = @projectPrefix + ' Beta ' + @timestamp;

-- Check if projects with similar names already exist
IF NOT EXISTS (SELECT 1 FROM Projects WHERE Name LIKE @projectPrefix + '%' + @timestamp)
BEGIN
    -- Insert sample projects
    INSERT INTO Projects (Name, Status, ClientName, Country, CreatedAt, UpdatedAt)
    VALUES
    (@project1Name, 0, 'National Infrastructure Authority', 'United Arab Emirates', GETUTCDATE(), GETUTCDATE()),
    (@project2Name, 0, 'Urban Development Corporation', 'United Arab Emirates', GETUTCDATE(), GETUTCDATE());

    DECLARE @project1Id INT = (SELECT Id FROM Projects WHERE Name = @project1Name);
    DECLARE @project2Id INT = (SELECT Id FROM Projects WHERE Name = @project2Name);

    PRINT 'Created projects:';
    PRINT '  ' + @project1Name + ' (ID: ' + CAST(@project1Id AS NVARCHAR(10)) + ')';
    PRINT '  ' + @project2Name + ' (ID: ' + CAST(@project2Id AS NVARCHAR(10)) + ')';

    -- Store project IDs for use in other scripts
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('PROJECT_1_ID', CAST(@project1Id AS NVARCHAR(10)), 'ID of the first seeded project'),
    ('PROJECT_2_ID', CAST(@project2Id AS NVARCHAR(10)), 'ID of the second seeded project'),
    ('PROJECT_1_NAME', @project1Name, 'Name of the first seeded project'),
    ('PROJECT_2_NAME', @project2Name, 'Name of the second seeded project');

    PRINT 'Project seeding completed successfully!';
END
ELSE
BEGIN
    PRINT 'Projects with timestamp ' + @timestamp + ' already exist. Skipping project creation.';

    -- Get existing project IDs
    DECLARE @existingProject1Id INT = (SELECT TOP 1 Id FROM Projects WHERE Name LIKE @projectPrefix + '%' ORDER BY Id);
    DECLARE @existingProject2Id INT = (SELECT Id FROM (SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn FROM Projects WHERE Name LIKE @projectPrefix + '%') ranked WHERE rn = 2);

    -- Update configuration with existing project IDs
    MERGE SeedConfiguration AS target
    USING (VALUES
        ('PROJECT_1_ID', CAST(@existingProject1Id AS NVARCHAR(10))),
        ('PROJECT_2_ID', CAST(@existingProject2Id AS NVARCHAR(10))),
        ('PROJECT_1_NAME', (SELECT Name FROM Projects WHERE Id = @existingProject1Id)),
        ('PROJECT_2_NAME', (SELECT Name FROM Projects WHERE Id = @existingProject2Id))
    ) AS source (ConfigKey, ConfigValue)
    ON target.ConfigKey = source.ConfigKey
    WHEN MATCHED THEN
        UPDATE SET ConfigValue = source.ConfigValue, UpdatedAt = GETUTCDATE()
    WHEN NOT MATCHED THEN
        INSERT (ConfigKey, ConfigValue, Description) VALUES (source.ConfigKey, source.ConfigValue, 'Existing project information');
END;