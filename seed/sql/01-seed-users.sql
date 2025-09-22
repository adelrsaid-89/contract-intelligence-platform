-- Seed Users Script
-- Creates sample users with different roles
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping user seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting user seeding...';

-- Variables for dynamic configuration
DECLARE @emailDomain NVARCHAR(100) = dbo.GetSeedConfig('USER_EMAIL_DOMAIN');
DECLARE @adminPassword NVARCHAR(100) = dbo.GetSeedConfig('ADMIN_DEFAULT_PASSWORD');
DECLARE @managerPassword NVARCHAR(100) = dbo.GetSeedConfig('MANAGER_DEFAULT_PASSWORD');
DECLARE @userPassword NVARCHAR(100) = dbo.GetSeedConfig('USER_DEFAULT_PASSWORD');

-- Hash passwords (simplified - in real implementation, use proper hashing)
-- For POC purposes, we'll use a simple approach
DECLARE @adminPasswordHash NVARCHAR(255) = HASHBYTES('SHA2_256', @adminPassword);
DECLARE @managerPasswordHash NVARCHAR(255) = HASHBYTES('SHA2_256', @managerPassword);
DECLARE @userPasswordHash NVARCHAR(255) = HASHBYTES('SHA2_256', @userPassword);

-- Check if users already exist (avoid duplicates)
IF NOT EXISTS (SELECT 1 FROM Users WHERE Email LIKE '%@' + @emailDomain)
BEGIN
    -- Insert Admin User
    INSERT INTO Users (Name, Email, Role, PasswordHash, IsActive, CreatedAt, UpdatedAt)
    VALUES
    ('System Administrator', 'admin@' + @emailDomain, 0, @adminPasswordHash, 1, GETUTCDATE(), GETUTCDATE());

    DECLARE @adminId INT = SCOPE_IDENTITY();
    PRINT 'Created Admin user with ID: ' + CAST(@adminId AS NVARCHAR(10));

    -- Insert Manager Users
    INSERT INTO Users (Name, Email, Role, PasswordHash, IsActive, CreatedAt, UpdatedAt)
    VALUES
    ('Sarah Johnson', 'sarah.johnson@' + @emailDomain, 1, @managerPasswordHash, 1, GETUTCDATE(), GETUTCDATE()),
    ('Michael Chen', 'michael.chen@' + @emailDomain, 1, @managerPasswordHash, 1, GETUTCDATE(), GETUTCDATE());

    DECLARE @manager1Id INT = (SELECT Id FROM Users WHERE Email = 'sarah.johnson@' + @emailDomain);
    DECLARE @manager2Id INT = (SELECT Id FROM Users WHERE Email = 'michael.chen@' + @emailDomain);

    PRINT 'Created Manager users with IDs: ' + CAST(@manager1Id AS NVARCHAR(10)) + ', ' + CAST(@manager2Id AS NVARCHAR(10));

    -- Insert Regular Users (Subcontractors)
    INSERT INTO Users (Name, Email, Role, PasswordHash, IsActive, CreatedAt, UpdatedAt)
    VALUES
    ('Ahmed Al-Rashid', 'ahmed.rashid@' + @emailDomain, 2, @userPasswordHash, 1, GETUTCDATE(), GETUTCDATE()),
    ('Maria Gonzalez', 'maria.gonzalez@' + @emailDomain, 2, @userPasswordHash, 1, GETUTCDATE(), GETUTCDATE()),
    ('David Smith', 'david.smith@' + @emailDomain, 2, @userPasswordHash, 1, GETUTCDATE(), GETUTCDATE());

    DECLARE @user1Id INT = (SELECT Id FROM Users WHERE Email = 'ahmed.rashid@' + @emailDomain);
    DECLARE @user2Id INT = (SELECT Id FROM Users WHERE Email = 'maria.gonzalez@' + @emailDomain);
    DECLARE @user3Id INT = (SELECT Id FROM Users WHERE Email = 'david.smith@' + @emailDomain);

    PRINT 'Created Regular users with IDs: ' + CAST(@user1Id AS NVARCHAR(10)) + ', ' + CAST(@user2Id AS NVARCHAR(10)) + ', ' + CAST(@user3Id AS NVARCHAR(10));

    -- Store user IDs for use in other scripts
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('ADMIN_USER_ID', CAST(@adminId AS NVARCHAR(10)), 'ID of the seeded admin user'),
    ('MANAGER_1_USER_ID', CAST(@manager1Id AS NVARCHAR(10)), 'ID of the first seeded manager user'),
    ('MANAGER_2_USER_ID', CAST(@manager2Id AS NVARCHAR(10)), 'ID of the second seeded manager user'),
    ('SUBCONTRACTOR_1_USER_ID', CAST(@user1Id AS NVARCHAR(10)), 'ID of the first seeded subcontractor user'),
    ('SUBCONTRACTOR_2_USER_ID', CAST(@user2Id AS NVARCHAR(10)), 'ID of the second seeded subcontractor user'),
    ('SUBCONTRACTOR_3_USER_ID', CAST(@user3Id AS NVARCHAR(10)), 'ID of the third seeded subcontractor user');

    PRINT 'User seeding completed successfully!';
    PRINT 'Default credentials:';
    PRINT '  Admin: admin@' + @emailDomain + ' / ' + @adminPassword;
    PRINT '  Managers: [manager]@' + @emailDomain + ' / ' + @managerPassword;
    PRINT '  Users: [user]@' + @emailDomain + ' / ' + @userPassword;
END
ELSE
BEGIN
    PRINT 'Users already exist for domain: ' + @emailDomain + '. Skipping user creation.';

    -- Update configuration with existing user IDs
    DECLARE @existingAdminId INT = (SELECT TOP 1 Id FROM Users WHERE Role = 0 AND Email LIKE '%@' + @emailDomain);
    DECLARE @existingManager1Id INT = (SELECT TOP 1 Id FROM Users WHERE Role = 1 AND Email LIKE '%@' + @emailDomain ORDER BY Id);
    DECLARE @existingManager2Id INT = (SELECT Id FROM (SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn FROM Users WHERE Role = 1 AND Email LIKE '%@' + @emailDomain) ranked WHERE rn = 2);
    DECLARE @existingUser1Id INT = (SELECT TOP 1 Id FROM Users WHERE Role = 2 AND Email LIKE '%@' + @emailDomain ORDER BY Id);
    DECLARE @existingUser2Id INT = (SELECT Id FROM (SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn FROM Users WHERE Role = 2 AND Email LIKE '%@' + @emailDomain) ranked WHERE rn = 2);
    DECLARE @existingUser3Id INT = (SELECT Id FROM (SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn FROM Users WHERE Role = 2 AND Email LIKE '%@' + @emailDomain) ranked WHERE rn = 3);

    -- Update or insert configuration
    MERGE SeedConfiguration AS target
    USING (VALUES
        ('ADMIN_USER_ID', CAST(@existingAdminId AS NVARCHAR(10))),
        ('MANAGER_1_USER_ID', CAST(@existingManager1Id AS NVARCHAR(10))),
        ('MANAGER_2_USER_ID', CAST(@existingManager2Id AS NVARCHAR(10))),
        ('SUBCONTRACTOR_1_USER_ID', CAST(@existingUser1Id AS NVARCHAR(10))),
        ('SUBCONTRACTOR_2_USER_ID', CAST(@existingUser2Id AS NVARCHAR(10))),
        ('SUBCONTRACTOR_3_USER_ID', CAST(@existingUser3Id AS NVARCHAR(10)))
    ) AS source (ConfigKey, ConfigValue)
    ON target.ConfigKey = source.ConfigKey
    WHEN MATCHED THEN
        UPDATE SET ConfigValue = source.ConfigValue, UpdatedAt = GETUTCDATE()
    WHEN NOT MATCHED THEN
        INSERT (ConfigKey, ConfigValue, Description) VALUES (source.ConfigKey, source.ConfigValue, 'ID of existing user');
END;