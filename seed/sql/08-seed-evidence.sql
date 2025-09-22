-- Seed Evidence Script
-- Creates sample evidence files uploaded by subcontractors for their assignments
-- Demonstrates file management and progress tracking
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping evidence seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting evidence seeding...';

-- Get user IDs from configuration
DECLARE @subcontractor1Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_1_USER_ID') AS INT);
DECLARE @subcontractor2Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_2_USER_ID') AS INT);
DECLARE @subcontractor3Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_3_USER_ID') AS INT);

-- Validate that we have the required IDs
IF @subcontractor1Id IS NULL OR @subcontractor2Id IS NULL OR @subcontractor3Id IS NULL
BEGIN
    PRINT 'ERROR: Missing required user IDs from configuration. Please run user seeding first.';
    RETURN;
END;

-- Get assignments to add evidence to
DECLARE @assignment1Id INT, @assignment2Id INT, @assignment3Id INT, @assignment4Id INT, @assignment5Id INT;

-- Get some assignments that have progress (In Progress or Done status)
SELECT TOP 5
    @assignment1Id = MIN(CASE WHEN rn = 1 THEN Id END),
    @assignment2Id = MIN(CASE WHEN rn = 2 THEN Id END),
    @assignment3Id = MIN(CASE WHEN rn = 3 THEN Id END),
    @assignment4Id = MIN(CASE WHEN rn = 4 THEN Id END),
    @assignment5Id = MIN(CASE WHEN rn = 5 THEN Id END)
FROM (
    SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn
    FROM Assignments
    WHERE Status IN (1, 2) -- In Progress or Done
    AND AssigneeUserId IN (@subcontractor1Id, @subcontractor2Id, @subcontractor3Id)
) ranked;

-- Check if evidence already exists
IF NOT EXISTS (SELECT 1 FROM Evidence WHERE AssignmentId IN (@assignment1Id, @assignment2Id, @assignment3Id, @assignment4Id, @assignment5Id))
AND @assignment1Id IS NOT NULL
BEGIN
    -- Create sample evidence files
    INSERT INTO Evidence (AssignmentId, FileName, FilePath, FileSize, ContentType, Description, UploadedBy, UploadedAt)
    VALUES
    -- Evidence for Assignment 1 (Progress reports)
    (@assignment1Id, 'monthly-progress-report-march-2024.pdf', '/seed/evidence/monthly-progress-report-march-2024.pdf', 245760, 'application/pdf', 'Monthly progress report for March 2024 including construction status, quality metrics, and safety statistics', @subcontractor1Id, GETUTCDATE()),
    (@assignment1Id, 'construction-photos-march-2024.zip', '/seed/evidence/construction-photos-march-2024.zip', 15728640, 'application/zip', 'Photographic evidence of construction progress for March 2024', @subcontractor1Id, DATEADD(hour, -2, GETUTCDATE())),

    -- Evidence for Assignment 2 (Completed subcontractor reports)
    (@assignment2Id, 'subcontractor-performance-summary-q1-2024.pdf', '/seed/evidence/subcontractor-performance-summary-q1-2024.pdf', 182340, 'application/pdf', 'Quarterly subcontractor performance summary including compliance metrics and recommendations', @subcontractor2Id, DATEADD(day, -1, GETUTCDATE())),
    (@assignment2Id, 'compliance-certificates-q1-2024.pdf', '/seed/evidence/compliance-certificates-q1-2024.pdf', 98567, 'application/pdf', 'Compliance certificates and audit results for Q1 2024', @subcontractor2Id, DATEADD(day, -1, GETUTCDATE())),

    -- Evidence for Assignment 3 (Insurance documentation)
    (@assignment3Id, 'insurance-renewal-certificate-2024.pdf', '/seed/evidence/insurance-renewal-certificate-2024.pdf', 156890, 'application/pdf', 'Updated insurance certificate and performance bond documentation', @subcontractor2Id, DATEADD(hour, -6, GETUTCDATE())),
    (@assignment3Id, 'bond-validation-letter.pdf', '/seed/evidence/bond-validation-letter.pdf', 87432, 'application/pdf', 'Performance bond validation letter from bonding company', @subcontractor2Id, DATEADD(hour, -5, GETUTCDATE())),

    -- Evidence for Assignment 4 (Environmental monitoring)
    (@assignment4Id, 'environmental-monitoring-report-week12.pdf', '/seed/evidence/environmental-monitoring-report-week12.pdf', 298754, 'application/pdf', 'Weekly environmental monitoring report including air quality, noise levels, and waste management data', @subcontractor3Id, DATEADD(day, -2, GETUTCDATE())),
    (@assignment4Id, 'water-usage-monitoring-charts.xlsx', '/seed/evidence/water-usage-monitoring-charts.xlsx', 145623, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Water usage monitoring data and spillage tracking charts', @subcontractor3Id, DATEADD(day, -2, GETUTCDATE())),

    -- Evidence for Assignment 5 (Quality audits)
    (@assignment5Id, 'quality-audit-checklist-march-2024.pdf', '/seed/evidence/quality-audit-checklist-march-2024.pdf', 201456, 'application/pdf', 'Completed quality audit checklist with inspection results and photographic evidence', @subcontractor1Id, DATEADD(hour, -12, GETUTCDATE())),
    (@assignment5Id, 'material-compliance-certificates.pdf', '/seed/evidence/material-compliance-certificates.pdf', 167893, 'application/pdf', 'Material compliance certificates and test results for March deliveries', @subcontractor1Id, DATEADD(hour, -11, GETUTCDATE())),

    -- Additional evidence types
    (@assignment1Id, 'safety-incident-log-march-2024.xlsx', '/seed/evidence/safety-incident-log-march-2024.xlsx', 67890, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Safety incident log and near-miss reports for March 2024', @subcontractor1Id, DATEADD(hour, -8, GETUTCDATE())),
    (@assignment2Id, 'vendor-performance-scorecard.pdf', '/seed/evidence/vendor-performance-scorecard.pdf', 123456, 'application/pdf', 'Vendor performance scorecard with KPI measurements and recommendations', @subcontractor2Id, DATEADD(hour, -4, GETUTCDATE())),
    (@assignment3Id, 'emergency-response-drill-video.mp4', '/seed/evidence/emergency-response-drill-video.mp4', 52428800, 'video/mp4', 'Emergency response drill video demonstrating evacuation procedures and response times', @subcontractor2Id, DATEADD(hour, -3, GETUTCDATE()));

    PRINT 'Evidence seeding completed successfully!';

    -- Display evidence summary
    SELECT
        u.Name as UploadedBy,
        a.Id as AssignmentId,
        o.Description as ObligationDescription,
        e.FileName,
        e.ContentType,
        FORMAT(e.FileSize / 1024.0, 'N0') + ' KB' as FileSize,
        e.Description as EvidenceDescription,
        FORMAT(e.UploadedAt, 'yyyy-MM-dd HH:mm') as UploadedAt
    FROM Evidence e
    INNER JOIN Users u ON e.UploadedBy = u.Id
    INNER JOIN Assignments a ON e.AssignmentId = a.Id
    INNER JOIN Obligations o ON a.ObligationId = o.Id
    WHERE e.AssignmentId IN (@assignment1Id, @assignment2Id, @assignment3Id, @assignment4Id, @assignment5Id)
    ORDER BY u.Name, a.Id, e.UploadedAt;

    -- Display file type distribution
    SELECT
        ContentType,
        COUNT(*) as FileCount,
        FORMAT(SUM(FileSize) / 1024.0 / 1024.0, 'N2') + ' MB' as TotalSize
    FROM Evidence e
    WHERE e.AssignmentId IN (@assignment1Id, @assignment2Id, @assignment3Id, @assignment4Id, @assignment5Id)
    GROUP BY ContentType
    ORDER BY COUNT(*) DESC;

    -- Store evidence information for reporting
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('SAMPLE_EVIDENCE_COUNT', CAST(@@ROWCOUNT AS NVARCHAR(10)), 'Number of sample evidence files created'),
    ('EVIDENCE_CREATED', 'true', 'Flag indicating evidence has been seeded');

    PRINT '';
    PRINT 'Evidence File Statistics:';
    PRINT 'Total Evidence Files: ' + CAST(@@ROWCOUNT AS NVARCHAR(10));
    PRINT 'File Types: PDF, Excel, ZIP, MP4';
    PRINT 'Average File Size: ' + FORMAT((SELECT AVG(CAST(FileSize AS FLOAT)) FROM Evidence WHERE AssignmentId IN (@assignment1Id, @assignment2Id, @assignment3Id, @assignment4Id, @assignment5Id)) / 1024.0, 'N0') + ' KB';
    PRINT '';
    PRINT 'Evidence demonstrates:';
    PRINT '- Multiple file types (documents, spreadsheets, images, videos)';
    PRINT '- Realistic file sizes and naming conventions';
    PRINT '- Progress tracking through evidence uploads';
    PRINT '- Different types of evidence for different obligation types';
    PRINT '- File metadata and descriptions for searchability';
END
ELSE
BEGIN
    PRINT 'Evidence already exists for these assignments. Skipping evidence creation.';

    -- Display existing evidence summary
    SELECT
        ContentType,
        COUNT(*) as FileCount,
        FORMAT(SUM(FileSize) / 1024.0 / 1024.0, 'N2') + ' MB' as TotalSize
    FROM Evidence e
    INNER JOIN Assignments a ON e.AssignmentId = a.Id
    INNER JOIN Obligations o ON a.ObligationId = o.Id
    INNER JOIN Contracts c ON o.ContractId = c.Id
    GROUP BY ContentType
    ORDER BY COUNT(*) DESC;
END;