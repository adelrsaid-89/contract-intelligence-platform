-- Seed Obligations Script
-- Creates sample obligations extracted from contracts
-- Simulates AI extraction with realistic frequencies and due dates
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping obligation seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting obligation seeding...';

-- Get contract IDs from configuration
DECLARE @contract1Id INT = CAST(dbo.GetSeedConfig('CONTRACT_1_ID') AS INT);
DECLARE @contract2Id INT = CAST(dbo.GetSeedConfig('CONTRACT_2_ID') AS INT);
DECLARE @adminId INT = CAST(dbo.GetSeedConfig('ADMIN_USER_ID') AS INT);

-- Validate that we have the required IDs
IF @contract1Id IS NULL OR @contract2Id IS NULL OR @adminId IS NULL
BEGIN
    PRINT 'ERROR: Missing required contract or user IDs from configuration. Please run previous seeding scripts first.';
    RETURN;
END;

-- Check if obligations already exist for these contracts
IF NOT EXISTS (SELECT 1 FROM Obligations WHERE ContractId IN (@contract1Id, @contract2Id))
BEGIN
    -- Insert obligations for Contract 1 (Transportation Hub)
    INSERT INTO Obligations (ContractId, Description, Frequency, DueDate, PenaltyText, Source, Confidence, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- Monthly obligations
    (@contract1Id, 'Submit comprehensive monthly progress reports detailing construction advancement, quality metrics, safety statistics, and financial status', 'Monthly', DATEADD(day, 5, DATEADD(month, 1, GETDATE())), '$10,000 for each day late', 0, 0.92, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'Provide monthly subcontractor performance reports including compliance with contract terms and performance metrics', 'Monthly', DATEADD(day, 10, DATEADD(month, 1, GETDATE())), '$20,000 per non-compliant subcontractor + remediation costs', 0, 0.89, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Quarterly obligations
    (@contract1Id, 'Conduct mandatory safety training for all personnel and maintain current safety certifications for equipment operators', 'Quarterly', DATEADD(day, 90, GETDATE()), '$25,000 per uncertified worker + work stoppage', 0, 0.94, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'Maintain adequate insurance coverage and performance bonds, providing updated certificates quarterly', 'Quarterly', DATEADD(day, 60, GETDATE()), 'Immediate work suspension + $50,000 daily penalty until compliance', 1, 0.97, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Weekly obligations
    (@contract1Id, 'Monitor and report environmental impact metrics including air quality, noise levels, waste management, and water usage', 'Weekly', DATEADD(day, 7, GETDATE()), '$15,000 per late report + regulatory compliance costs', 0, 0.88, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Bi-weekly obligations
    (@contract1Id, 'Perform comprehensive quality control inspections for all major construction phases with detailed reports and photographic evidence', 'Bi-weekly', DATEADD(day, 14, GETDATE()), '5% payment reduction for failed inspections', 0, 0.91, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Milestone-based obligations
    (@contract1Id, 'Complete and deliver all project milestones according to approved schedule including design approvals, construction phases, and testing procedures', 'Per milestone schedule', DATEADD(month, 6, GETDATE()), '1% of total contract value per week delay + liquidated damages', 1, 0.96, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'Integrate all technological systems including baggage handling, security, and navigation systems with comprehensive testing and documentation', 'Per system delivery', DATEADD(month, 30, GETDATE()), '$100,000 per day delay in operational readiness', 0, 0.87, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId);

    -- Insert obligations for Contract 2 (Commercial Mall)
    INSERT INTO Obligations (ContractId, Description, Frequency, DueDate, PenaltyText, Source, Confidence, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- Bi-weekly obligations
    (@contract2Id, 'Submit detailed bi-weekly progress reports including construction status, quality metrics, safety records, and financial tracking with photographic evidence', 'Bi-weekly', DATEADD(day, 14, GETDATE()), '$7,500 for each day late', 0, 0.93, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Weekly obligations
    (@contract2Id, 'Conduct comprehensive weekly safety inspections of all work areas, equipment, and personnel compliance with safety protocols', 'Weekly', DATEADD(day, 7, GETDATE()), '$15,000 per missed inspection + work suspension', 1, 0.95, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Monthly obligations
    (@contract2Id, 'Perform monthly quality audits covering workmanship, materials compliance, and adherence to specifications with third-party verification', 'Monthly', DATEADD(day, 30, GETDATE()), '3% payment reduction for failed audits + remedial work costs', 0, 0.90, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Develop and maintain comprehensive emergency response plans and conduct monthly emergency drills with all personnel', 'Monthly', DATEADD(day, 15, DATEADD(month, 1, GETDATE())), '$18,000 per missed drill + safety compliance review', 0, 0.86, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Daily obligations
    (@contract2Id, 'Monitor and maintain environmental compliance including noise control, dust management, and waste disposal according to local regulations', 'Daily', DATEADD(day, 1, GETDATE()), '$12,000 per violation + regulatory fines', 0, 0.91, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Maintain water systems including plumbing, sprinkler systems, and decorative fountains with minimal spillage and optimal pressure', 'Daily', DATEADD(day, 1, GETDATE()), '$3,000 per day for spillage exceeding 3 liters', 1, 0.94, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Milestone-based obligations
    (@contract2Id, 'Complete retail spaces according to tenant requirements and approved specifications, ensuring all utilities and systems are operational', 'Per delivery schedule', DATEADD(month, 18, GETDATE()), '$25,000 per day delay per retail unit', 0, 0.88, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Test and commission all building systems including HVAC, electrical, fire safety, and security systems with full documentation', 'Per system completion', DATEADD(month, 20, GETDATE()), '$40,000 per day delay in operational readiness', 1, 0.92, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Ensure parking facility construction meets capacity requirements and traffic flow specifications with proper signage and safety features', 'Milestone-based', DATEADD(month, 15, GETDATE()), '$20,000 per parking space below requirement', 0, 0.89, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Coordinate with individual tenants for fit-out requirements, utility connections, and space modifications according to lease agreements', 'As required per tenant', DATEADD(month, 12, GETDATE()), '$10,000 per tenant delay + tenant compensation costs', 0, 0.85, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId);

    -- Get the obligation IDs for configuration storage
    DECLARE @obligation1Id INT = (SELECT TOP 1 Id FROM Obligations WHERE ContractId = @contract1Id ORDER BY Id);
    DECLARE @obligation2Id INT = (SELECT TOP 1 Id FROM Obligations WHERE ContractId = @contract2Id ORDER BY Id);

    -- Store obligation IDs for use in assignment scripts
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('FIRST_OBLIGATION_CONTRACT_1', CAST(@obligation1Id AS NVARCHAR(10)), 'First obligation ID for contract 1'),
    ('FIRST_OBLIGATION_CONTRACT_2', CAST(@obligation2Id AS NVARCHAR(10)), 'First obligation ID for contract 2');

    PRINT 'Obligation seeding completed successfully!';

    -- Display summary
    SELECT
        c.Title,
        COUNT(o.Id) as ObligationCount,
        AVG(o.Confidence) as AverageConfidence,
        SUM(CASE WHEN o.Source = 0 THEN 1 ELSE 0 END) as AIExtracted,
        SUM(CASE WHEN o.Source = 1 THEN 1 ELSE 0 END) as HumanVerified
    FROM Contracts c
    LEFT JOIN Obligations o ON c.Id = o.ContractId
    WHERE c.Id IN (@contract1Id, @contract2Id)
    GROUP BY c.Id, c.Title;

    -- Display frequency distribution
    SELECT
        Frequency,
        COUNT(*) as Count
    FROM Obligations
    WHERE ContractId IN (@contract1Id, @contract2Id)
    GROUP BY Frequency
    ORDER BY Count DESC;

    PRINT 'Coverage Analysis:';
    PRINT 'Transportation Hub Contract: ' + CAST((SELECT COUNT(*) FROM Obligations WHERE ContractId = @contract1Id) AS NVARCHAR(10)) + ' obligations extracted';
    PRINT 'Commercial Mall Contract: ' + CAST((SELECT COUNT(*) FROM Obligations WHERE ContractId = @contract2Id) AS NVARCHAR(10)) + ' obligations extracted';
    PRINT 'Overall AI Extraction Accuracy: 90.5% (simulated)';
    PRINT 'Coverage Rate: 85.7% (simulated)';
END
ELSE
BEGIN
    PRINT 'Obligations already exist for these contracts. Skipping obligation creation.';

    -- Display existing obligations summary
    SELECT
        c.Title,
        COUNT(o.Id) as ObligationCount,
        AVG(o.Confidence) as AverageConfidence,
        SUM(CASE WHEN o.Source = 0 THEN 1 ELSE 0 END) as AIExtracted,
        SUM(CASE WHEN o.Source = 1 THEN 1 ELSE 0 END) as HumanVerified
    FROM Contracts c
    LEFT JOIN Obligations o ON c.Id = o.ContractId
    WHERE c.Id IN (@contract1Id, @contract2Id)
    GROUP BY c.Id, c.Title;
END;