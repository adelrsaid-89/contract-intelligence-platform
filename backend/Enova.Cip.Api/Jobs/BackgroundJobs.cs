using Hangfire;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Interfaces;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Api.Jobs;

public interface IBackgroundJobService
{
    Task ScheduleAssignmentEmailJob(int assignmentId);
    Task ScheduleReminderJobs();
    Task SchedulePenaltyRiskJobs();
    Task ScheduleSearchIndexerJobs();
    Task ScheduleNotificationCleanupJobs();
}

public class BackgroundJobService : IBackgroundJobService
{
    private readonly IBackgroundJobClient _backgroundJobClient;
    private readonly IRecurringJobManager _recurringJobManager;

    public BackgroundJobService(IBackgroundJobClient backgroundJobClient, IRecurringJobManager recurringJobManager)
    {
        _backgroundJobClient = backgroundJobClient;
        _recurringJobManager = recurringJobManager;
    }

    public Task ScheduleAssignmentEmailJob(int assignmentId)
    {
        _backgroundJobClient.Enqueue<AssignmentEmailJob>(job => job.ExecuteAsync(assignmentId));
        return Task.CompletedTask;
    }

    public Task ScheduleReminderJobs()
    {
        _recurringJobManager.AddOrUpdate<ReminderJob>(
            "reminder-job",
            job => job.ExecuteAsync(),
            Cron.Daily(9)); // Run daily at 9 AM
        return Task.CompletedTask;
    }

    public Task SchedulePenaltyRiskJobs()
    {
        _recurringJobManager.AddOrUpdate<PenaltyRiskJob>(
            "penalty-risk-job",
            job => job.ExecuteAsync(),
            Cron.Daily(10)); // Run daily at 10 AM
        return Task.CompletedTask;
    }

    public Task ScheduleSearchIndexerJobs()
    {
        _recurringJobManager.AddOrUpdate<SearchIndexerJob>(
            "search-indexer-job",
            job => job.ExecuteAsync(),
            Cron.Hourly()); // Run every hour
        return Task.CompletedTask;
    }

    public Task ScheduleNotificationCleanupJobs()
    {
        _recurringJobManager.AddOrUpdate<NotificationCleanupJob>(
            "notification-cleanup-job",
            job => job.ExecuteAsync(),
            Cron.Weekly(DayOfWeek.Sunday, 2)); // Run weekly on Sunday at 2 AM
        return Task.CompletedTask;
    }
}

public class AssignmentEmailJob
{
    private readonly INotificationService _notificationService;
    private readonly ILogger<AssignmentEmailJob> _logger;

    public AssignmentEmailJob(INotificationService notificationService, ILogger<AssignmentEmailJob> logger)
    {
        _notificationService = notificationService;
        _logger = logger;
    }

    public async Task ExecuteAsync(int assignmentId)
    {
        try
        {
            await _notificationService.SendAssignmentNotificationAsync(assignmentId);
            _logger.LogInformation("Assignment notification sent for assignment {AssignmentId}", assignmentId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send assignment notification for assignment {AssignmentId}", assignmentId);
            throw;
        }
    }
}

public class ReminderJob
{
    private readonly INotificationService _notificationService;
    private readonly ILogger<ReminderJob> _logger;

    public ReminderJob(INotificationService notificationService, ILogger<ReminderJob> logger)
    {
        _notificationService = notificationService;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        try
        {
            await _notificationService.SendReminderNotificationsAsync();
            _logger.LogInformation("Reminder notifications job completed");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute reminder notifications job");
            throw;
        }
    }
}

public class PenaltyRiskJob
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly INotificationService _notificationService;
    private readonly ILogger<PenaltyRiskJob> _logger;

    public PenaltyRiskJob(IUnitOfWork unitOfWork, INotificationService notificationService, ILogger<PenaltyRiskJob> logger)
    {
        _unitOfWork = unitOfWork;
        _notificationService = notificationService;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        try
        {
            // Find overdue assignments
            var overdueAssignments = await _unitOfWork.Assignments.FindAsync(
                a => a.Status == AssignmentStatus.Overdue);

            foreach (var assignment in overdueAssignments)
            {
                // Calculate penalty risk for the obligation
                var obligation = await _unitOfWork.Obligations.GetByIdAsync(assignment.ObligationId);
                if (obligation != null)
                {
                    await _notificationService.SendPenaltyRiskNotificationAsync(obligation.Id);
                }
            }

            _logger.LogInformation("Penalty risk job completed, processed {Count} overdue assignments", overdueAssignments.Count());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute penalty risk job");
            throw;
        }
    }
}

public class SearchIndexerJob
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly ISearchService _searchService;
    private readonly ILogger<SearchIndexerJob> _logger;

    public SearchIndexerJob(IUnitOfWork unitOfWork, ISearchService searchService, ILogger<SearchIndexerJob> logger)
    {
        _unitOfWork = unitOfWork;
        _searchService = searchService;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        try
        {
            // Index contracts
            var contracts = await _unitOfWork.Contracts.GetAllAsync();
            var contractDocuments = contracts.Select(c => (c.Id.ToString(), c));
            await _searchService.BulkIndexAsync("contracts", contractDocuments);

            // Index obligations
            var obligations = await _unitOfWork.Obligations.GetAllAsync();
            var obligationDocuments = obligations.Select(o => (o.Id.ToString(), o));
            await _searchService.BulkIndexAsync("obligations", obligationDocuments);

            _logger.LogInformation("Search indexer job completed, indexed {ContractCount} contracts and {ObligationCount} obligations",
                contracts.Count(), obligations.Count());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute search indexer job");
            throw;
        }
    }
}

public class NotificationCleanupJob
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<NotificationCleanupJob> _logger;

    public NotificationCleanupJob(IUnitOfWork unitOfWork, ILogger<NotificationCleanupJob> logger)
    {
        _unitOfWork = unitOfWork;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        try
        {
            // Delete notifications older than 90 days
            var cutoffDate = DateTime.UtcNow.AddDays(-90);
            var oldNotifications = await _unitOfWork.Notifications.FindAsync(
                n => n.CreatedAt < cutoffDate);

            if (oldNotifications.Any())
            {
                await _unitOfWork.Notifications.DeleteRangeAsync(oldNotifications);
                await _unitOfWork.SaveChangesAsync();

                _logger.LogInformation("Notification cleanup job completed, deleted {Count} old notifications", oldNotifications.Count());
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute notification cleanup job");
            throw;
        }
    }
}