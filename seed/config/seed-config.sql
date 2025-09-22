-- Seed Configuration Script
-- This script sets up configuration for seed data generation
-- Supports SEED_MODE environment variable: none, example

-- Create configuration table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SeedConfiguration')
BEGIN
    CREATE TABLE SeedConfiguration (
        Id int IDENTITY(1,1) PRIMARY KEY,
        ConfigKey NVARCHAR(100) NOT NULL UNIQUE,
        ConfigValue NVARCHAR(MAX),
        Description NVARCHAR(500),
        CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
        UpdatedAt DATETIME2 DEFAULT GETUTCDATE()
    );
END;

-- Clear existing configuration
DELETE FROM SeedConfiguration;

-- Insert default configuration
INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
('SEED_MODE', 'example', 'Seed mode: none (no seed data) or example (sample data)'),
('PROJECT_PREFIX', 'Project', 'Prefix for auto-generated project names'),
('USER_EMAIL_DOMAIN', 'example.com', 'Domain for auto-generated user emails'),
('CONTRACT_FILE_PATH', '/seed/contracts/', 'Path to sample contract files'),
('ADMIN_DEFAULT_PASSWORD', 'Admin123!', 'Default password for admin user (should be changed)'),
('MANAGER_DEFAULT_PASSWORD', 'Manager123!', 'Default password for manager users'),
('USER_DEFAULT_PASSWORD', 'User123!', 'Default password for regular users');

-- Function to get configuration value
IF OBJECT_ID('dbo.GetSeedConfig', 'FN') IS NOT NULL
    DROP FUNCTION dbo.GetSeedConfig;
GO

CREATE FUNCTION dbo.GetSeedConfig(@key NVARCHAR(100))
RETURNS NVARCHAR(MAX)
AS
BEGIN
    DECLARE @value NVARCHAR(MAX);
    SELECT @value = ConfigValue FROM SeedConfiguration WHERE ConfigKey = @key;
    RETURN @value;
END;
GO

-- Function to check if seeding should be performed
IF OBJECT_ID('dbo.ShouldSeed', 'FN') IS NOT NULL
    DROP FUNCTION dbo.ShouldSeed;
GO

CREATE FUNCTION dbo.ShouldSeed()
RETURNS BIT
AS
BEGIN
    DECLARE @seedMode NVARCHAR(50);
    SELECT @seedMode = dbo.GetSeedConfig('SEED_MODE');

    IF @seedMode = 'none'
        RETURN 0;
    ELSE
        RETURN 1;
END;
GO

PRINT 'Seed configuration completed. Current SEED_MODE: ' + dbo.GetSeedConfig('SEED_MODE');