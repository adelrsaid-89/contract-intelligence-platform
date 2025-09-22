-- Seed Contract Metadata Script
-- Creates sample metadata extracted from contracts
-- Simulates AI extraction with high confidence scores
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping metadata seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting metadata seeding...';

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

-- Check if metadata already exists for these contracts
IF NOT EXISTS (SELECT 1 FROM MetadataFields WHERE ContractId IN (@contract1Id, @contract2Id))
BEGIN
    -- Insert metadata for Contract 1 (Transportation Hub)
    INSERT INTO MetadataFields (ContractId, [Key], [Value], Source, Confidence, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- AI-extracted metadata with high confidence
    (@contract1Id, 'ProjectName', 'Regional Transportation Hub Development', 0, 0.95, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'ClientName', 'National Infrastructure Authority', 0, 0.98, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'ContractValue', '45750000', 0, 0.99, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'StartDate', '2024-03-01', 0, 0.97, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'EndDate', '2027-02-28', 0, 0.97, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'Country', 'United Arab Emirates', 0, 0.96, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'PaymentTerms', 'Monthly progress payments within 30 days of invoice', 0, 0.92, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'ContractNumber', 'TH-2024-001', 0, 0.99, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'Contractor', 'Global Construction Consortium LLC', 0, 0.94, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Human-verified metadata (higher confidence)
    (@contract1Id, 'ListOfServices', 'Architectural and engineering design services, Site preparation and earthworks, Construction of terminal buildings, Runway and taxiway construction, Installation of navigation and communication systems, Baggage handling system installation, Fire safety and security systems, Landscaping and external works, 24-month maintenance and warranty services', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'KPIs', 'Construction Quality Index ≥ 95%, Safety Incident Rate ≤ 0.5 per 100,000 hours, Schedule Adherence ≥ 98%, Environmental Compliance 100%, Water Management Efficiency ≤ 5 liters spillage per day', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract1Id, 'PenaltyClauses', 'Liquidated damages: 0.5% per week delay (max 10%), Performance penalties per KPI targets, Safety violations: $100,000 + suspension, Environmental non-compliance: penalties + remediation costs', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId);

    -- Insert metadata for Contract 2 (Commercial Mall)
    INSERT INTO MetadataFields (ContractId, [Key], [Value], Source, Confidence, CreatedAt, UpdatedAt, CreatedBy, UpdatedBy)
    VALUES
    -- AI-extracted metadata
    (@contract2Id, 'ProjectName', 'Metropolitan Shopping Center Development', 0, 0.94, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'ClientName', 'Urban Development Corporation', 0, 0.97, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'ContractValue', '28950000', 0, 0.99, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'StartDate', '2024-06-15', 0, 0.96, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'EndDate', '2026-05-30', 0, 0.96, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Country', 'United Arab Emirates', 0, 0.95, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'PaymentTerms', 'Bi-weekly progress payments within 21 days of invoice', 0, 0.91, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'ContractNumber', 'CRC-2024-002', 0, 0.99, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'Contractor', 'Premier Commercial Builders Ltd', 0, 0.93, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),

    -- Human-verified metadata
    (@contract2Id, 'ListOfServices', 'Architectural design and space planning, Structural engineering and foundation work, Main retail building construction, Entertainment complex construction, Multi-level parking structure, HVAC system design and installation, Electrical and lighting systems, Fire safety and security systems, Retail fit-out coordination, Landscaping and exterior amenities, 12-month defects liability period', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'KPIs', 'Construction Quality Score ≥ 92%, Safety Performance Index ≤ 1.0 per 100,000 hours, Schedule Performance ≥ 96%, Waste Management Efficiency ≥ 85% recycling rate, Energy System Performance ≥ 98% availability', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId),
    (@contract2Id, 'PenaltyClauses', 'Liquidated damages: 0.3% per week delay (max 8%), Quality non-compliance: remedial work + 5% penalty, Safety incidents: $75,000 + suspension, Tenant delay penalties: lost rent + compensation', 1, 1.0, GETUTCDATE(), GETUTCDATE(), @adminId, @adminId);

    PRINT 'Metadata seeding completed successfully!';
    PRINT 'Created ' + CAST(@@ROWCOUNT AS NVARCHAR(10)) + ' metadata fields across both contracts';

    -- Display summary
    SELECT
        c.Title,
        COUNT(mf.Id) as MetadataFieldCount,
        AVG(mf.Confidence) as AverageConfidence,
        SUM(CASE WHEN mf.Source = 0 THEN 1 ELSE 0 END) as AIExtracted,
        SUM(CASE WHEN mf.Source = 1 THEN 1 ELSE 0 END) as HumanVerified
    FROM Contracts c
    LEFT JOIN MetadataFields mf ON c.Id = mf.ContractId
    WHERE c.Id IN (@contract1Id, @contract2Id)
    GROUP BY c.Id, c.Title;
END
ELSE
BEGIN
    PRINT 'Metadata already exists for these contracts. Skipping metadata creation.';

    -- Display existing metadata summary
    SELECT
        c.Title,
        COUNT(mf.Id) as MetadataFieldCount,
        AVG(mf.Confidence) as AverageConfidence,
        SUM(CASE WHEN mf.Source = 0 THEN 1 ELSE 0 END) as AIExtracted,
        SUM(CASE WHEN mf.Source = 1 THEN 1 ELSE 0 END) as HumanVerified
    FROM Contracts c
    LEFT JOIN MetadataFields mf ON c.Id = mf.ContractId
    WHERE c.Id IN (@contract1Id, @contract2Id)
    GROUP BY c.Id, c.Title;
END;