-- Seed Notifications Script
-- Creates sample notifications for various events (assignments, reminders, overdue)
-- Demonstrates the notification system and user communication
-- Respects SEED_MODE configuration

-- Only proceed if seeding is enabled
IF dbo.ShouldSeed() = 0
BEGIN
    PRINT 'Skipping notification seeding - SEED_MODE is set to none';
    RETURN;
END;

PRINT 'Starting notification seeding...';

-- Get user IDs from configuration
DECLARE @adminId INT = CAST(dbo.GetSeedConfig('ADMIN_USER_ID') AS INT);
DECLARE @manager1Id INT = CAST(dbo.GetSeedConfig('MANAGER_1_USER_ID') AS INT);
DECLARE @manager2Id INT = CAST(dbo.GetSeedConfig('MANAGER_2_USER_ID') AS INT);
DECLARE @subcontractor1Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_1_USER_ID') AS INT);
DECLARE @subcontractor2Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_2_USER_ID') AS INT);
DECLARE @subcontractor3Id INT = CAST(dbo.GetSeedConfig('SUBCONTRACTOR_3_USER_ID') AS INT);

-- Validate that we have the required IDs
IF @adminId IS NULL OR @manager1Id IS NULL OR @manager2Id IS NULL OR @subcontractor1Id IS NULL
BEGIN
    PRINT 'ERROR: Missing required user IDs from configuration. Please run user seeding first.';
    RETURN;
END;

-- Get some assignment IDs for reference
DECLARE @assignment1Id INT, @assignment2Id INT, @assignment3Id INT;
SELECT TOP 3
    @assignment1Id = MIN(CASE WHEN rn = 1 THEN Id END),
    @assignment2Id = MIN(CASE WHEN rn = 2 THEN Id END),
    @assignment3Id = MIN(CASE WHEN rn = 3 THEN Id END)
FROM (
    SELECT Id, ROW_NUMBER() OVER (ORDER BY Id) as rn
    FROM Assignments
    WHERE AssigneeUserId IN (@subcontractor1Id, @subcontractor2Id, @subcontractor3Id)
) ranked;

-- Check if notifications already exist
IF NOT EXISTS (SELECT 1 FROM Notifications WHERE UserId IN (@manager1Id, @manager2Id, @subcontractor1Id, @subcontractor2Id, @subcontractor3Id))
BEGIN
    -- Create various types of notifications
    INSERT INTO Notifications (UserId, Type, Title, Message, RelatedEntityType, RelatedEntityId, IsRead, Status, CreatedAt, ScheduledFor)
    VALUES
    -- Assignment created notifications (sent to assignees)
    (@subcontractor1Id, 0, 'New Assignment: Monthly Progress Reports', 'You have been assigned a new obligation: Submit comprehensive monthly progress reports detailing construction advancement, quality metrics, safety statistics, and financial status. Due date: ' + FORMAT(DATEADD(day, 5, GETDATE()), 'MMM dd, yyyy'), 'Assignment', @assignment1Id, 0, 1, DATEADD(hour, -24, GETUTCDATE()), DATEADD(hour, -24, GETUTCDATE())),

    (@subcontractor2Id, 0, 'New Assignment: Insurance Documentation', 'You have been assigned a new obligation: Maintain adequate insurance coverage and performance bonds, providing updated certificates quarterly. Due date: ' + FORMAT(DATEADD(day, 60, GETDATE()), 'MMM dd, yyyy'), 'Assignment', @assignment2Id, 1, 1, DATEADD(hour, -18, GETUTCDATE()), DATEADD(hour, -18, GETUTCDATE())),

    (@subcontractor3Id, 0, 'New Assignment: Environmental Monitoring', 'You have been assigned a new obligation: Monitor and report environmental impact metrics including air quality, noise levels, waste management, and water usage. Due date: ' + FORMAT(DATEADD(day, 7, GETDATE()), 'MMM dd, yyyy'), 'Assignment', @assignment3Id, 0, 1, DATEADD(hour, -12, GETUTCDATE()), DATEADD(hour, -12, GETUTCDATE())),

    -- Assignment reminder notifications (T-14 days and approaching deadlines)
    (@subcontractor1Id, 1, 'Reminder: Monthly Progress Reports Due Soon', 'This is a reminder that your monthly progress report is due in 5 days. Please ensure you have all necessary documentation and submit on time to avoid penalties.', 'Assignment', @assignment1Id, 0, 1, DATEADD(hour, -6, GETUTCDATE()), DATEADD(hour, -6, GETUTCDATE())),

    (@subcontractor2Id, 1, 'Reminder: Insurance Certificates Due in 2 Weeks', 'Your insurance and bonding certificates are due for renewal in 2 weeks. Please coordinate with your insurance provider to ensure timely submission.', 'Assignment', @assignment2Id, 1, 1, DATEADD(hour, -4, GETUTCDATE()), DATEADD(hour, -4, GETUTCDATE())),

    (@subcontractor3Id, 1, 'Urgent: Environmental Report Due Tomorrow', 'Your weekly environmental monitoring report is due tomorrow. Please complete the air quality measurements and submit the report by Friday 5:00 PM.', 'Assignment', @assignment3Id, 0, 1, DATEADD(hour, -2, GETUTCDATE()), DATEADD(hour, -2, GETUTCDATE())),

    -- Overdue notifications (sent to assignees and managers)
    (@subcontractor1Id, 2, 'OVERDUE: Monthly Progress Report', 'Your monthly progress report was due yesterday. Please submit immediately to minimize penalty charges. Current penalty: $10,000 per day late.', 'Assignment', @assignment1Id, 0, 1, DATEADD(hour, -1, GETUTCDATE()), DATEADD(hour, -1, GETUTCDATE())),

    (@manager1Id, 2, 'Team Member Overdue: Monthly Progress Report', 'Assignment for monthly progress report is now overdue. Assignee: ' + (SELECT Name FROM Users WHERE Id = @subcontractor1Id) + '. Please follow up immediately.', 'Assignment', @assignment1Id, 0, 1, DATEADD(hour, -1, GETUTCDATE()), DATEADD(hour, -1, GETUTCDATE())),

    -- Contract expiring notifications (sent to managers and admin)
    (@manager1Id, 3, 'Contract Milestone Approaching', 'Transportation Hub contract has an important milestone approaching in 30 days. Please review project progress and ensure all deliverables are on track.', 'Contract', CAST(dbo.GetSeedConfig('CONTRACT_1_ID') AS INT), 1, 1, DATEADD(hour, -8, GETUTCDATE()), DATEADD(hour, -8, GETUTCDATE())),

    (@manager2Id, 3, 'Contract Review Required', 'Commercial Mall contract requires quarterly review. Please assess progress against milestones and update stakeholders.', 'Contract', CAST(dbo.GetSeedConfig('CONTRACT_2_ID') AS INT), 0, 1, DATEADD(hour, -10, GETUTCDATE()), DATEADD(hour, -10, GETUTCDATE())),

    -- Penalty risk notifications (sent to managers and admin)
    (@manager1Id, 4, 'Penalty Risk Alert: Environmental Compliance', 'High penalty risk detected for environmental compliance obligations. Multiple late submissions may result in significant financial exposure.', 'Project', CAST(dbo.GetSeedConfig('PROJECT_1_ID') AS INT), 0, 1, DATEADD(hour, -3, GETUTCDATE()), DATEADD(hour, -3, GETUTCDATE())),

    (@adminId, 4, 'Portfolio Penalty Risk Summary', 'Weekly penalty risk summary: 3 obligations at high risk, potential exposure $75,000. Recommend immediate management intervention.', 'Portfolio', NULL, 1, 1, DATEADD(hour, -5, GETUTCDATE()), DATEADD(hour, -5, GETUTCDATE())),

    -- General notifications (system updates, announcements)
    (@adminId, 5, 'System Update: AI Extraction Completed', 'AI metadata and obligation extraction has been completed for all uploaded contracts. Review accuracy: 92.5%. Please review and approve extracted data.', 'System', NULL, 1, 1, DATEADD(hour, -48, GETUTCDATE()), DATEADD(hour, -48, GETUTCDATE())),

    (@manager1Id, 5, 'New Dashboard Features Available', 'New penalty risk analytics and progress tracking features are now available in your manager dashboard. Check out the enhanced reporting capabilities.', 'System', NULL, 0, 1, DATEADD(hour, -36, GETUTCDATE()), DATEADD(hour, -36, GETUTCDATE())),

    (@manager2Id, 5, 'Monthly Project Review Scheduled', 'Your monthly project review meeting is scheduled for next week. Please prepare progress reports and stakeholder updates.', 'Meeting', NULL, 0, 1, DATEADD(hour, -24, GETUTCDATE()), DATEADD(hour, -24, GETUTCDATE())),

    -- Evidence submission confirmations
    (@subcontractor2Id, 5, 'Evidence Upload Confirmed', 'Your evidence submission for insurance documentation has been received and is under manager review. Thank you for your timely submission.', 'Evidence', NULL, 1, 1, DATEADD(hour, -6, GETUTCDATE()), DATEADD(hour, -6, GETUTCDATE())),

    -- Success notifications (completed assignments)
    (@subcontractor2Id, 5, 'Assignment Completed Successfully', 'Your subcontractor performance report assignment has been approved and marked as complete. Excellent work!', 'Assignment', @assignment2Id, 1, 1, DATEADD(day, -1, GETUTCDATE()), DATEADD(day, -1, GETUTCDATE())),

    (@manager2Id, 5, 'Assignment Approved', 'Subcontractor assignment for performance reporting has been completed and approved. All requirements met successfully.', 'Assignment', @assignment2Id, 1, 1, DATEADD(day, -1, GETUTCDATE()), DATEADD(day, -1, GETUTCDATE()));

    PRINT 'Notification seeding completed successfully!';

    -- Display notification summary by type
    SELECT
        CASE n.Type
            WHEN 0 THEN 'Assignment Created'
            WHEN 1 THEN 'Assignment Reminder'
            WHEN 2 THEN 'Assignment Overdue'
            WHEN 3 THEN 'Contract Expiring'
            WHEN 4 THEN 'Penalty Risk'
            WHEN 5 THEN 'General'
        END as NotificationType,
        COUNT(*) as Count,
        SUM(CASE WHEN n.IsRead = 1 THEN 1 ELSE 0 END) as ReadCount,
        SUM(CASE WHEN n.IsRead = 0 THEN 1 ELSE 0 END) as UnreadCount
    FROM Notifications n
    WHERE n.UserId IN (@adminId, @manager1Id, @manager2Id, @subcontractor1Id, @subcontractor2Id, @subcontractor3Id)
    GROUP BY n.Type
    ORDER BY n.Type;

    -- Display notification summary by user
    SELECT
        u.Name as UserName,
        ur.Role as UserRole,
        COUNT(*) as TotalNotifications,
        SUM(CASE WHEN n.IsRead = 1 THEN 1 ELSE 0 END) as ReadNotifications,
        SUM(CASE WHEN n.IsRead = 0 THEN 1 ELSE 0 END) as UnreadNotifications
    FROM Notifications n
    INNER JOIN Users u ON n.UserId = u.Id
    INNER JOIN (VALUES
        (0, 'Admin'),
        (1, 'Manager'),
        (2, 'Subcontractor')
    ) ur(RoleId, Role) ON u.Role = ur.RoleId
    WHERE n.UserId IN (@adminId, @manager1Id, @manager2Id, @subcontractor1Id, @subcontractor2Id, @subcontractor3Id)
    GROUP BY u.Id, u.Name, ur.Role
    ORDER BY ur.RoleId, u.Name;

    -- Store notification information
    INSERT INTO SeedConfiguration (ConfigKey, ConfigValue, Description) VALUES
    ('SAMPLE_NOTIFICATION_COUNT', CAST(@@ROWCOUNT AS NVARCHAR(10)), 'Number of sample notifications created'),
    ('NOTIFICATIONS_CREATED', 'true', 'Flag indicating notifications have been seeded');

    PRINT '';
    PRINT 'Notification Statistics:';
    PRINT 'Total Notifications: ' + CAST(@@ROWCOUNT AS NVARCHAR(10));
    PRINT '';
    PRINT 'Notifications demonstrate:';
    PRINT '- Assignment creation and reminder workflows';
    PRINT '- Overdue penalty risk management';
    PRINT '- Multi-user notification distribution';
    PRINT '- Read/unread status tracking';
    PRINT '- Different notification priorities and types';
    PRINT '- Manager and subcontractor communication flows';
END
ELSE
BEGIN
    PRINT 'Notifications already exist for these users. Skipping notification creation.';

    -- Display existing notification summary
    SELECT
        CASE n.Type
            WHEN 0 THEN 'Assignment Created'
            WHEN 1 THEN 'Assignment Reminder'
            WHEN 2 THEN 'Assignment Overdue'
            WHEN 3 THEN 'Contract Expiring'
            WHEN 4 THEN 'Penalty Risk'
            WHEN 5 THEN 'General'
        END as NotificationType,
        COUNT(*) as Count,
        SUM(CASE WHEN n.IsRead = 1 THEN 1 ELSE 0 END) as ReadCount
    FROM Notifications n
    WHERE n.UserId IN (@adminId, @manager1Id, @manager2Id, @subcontractor1Id, @subcontractor2Id, @subcontractor3Id)
    GROUP BY n.Type
    ORDER BY COUNT(*) DESC;
END;