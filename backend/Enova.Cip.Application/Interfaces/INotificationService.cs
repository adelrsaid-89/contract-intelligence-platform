using Enova.Cip.Application.DTOs;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.Interfaces;

public interface INotificationService
{
    Task<IEnumerable<NotificationDto>> GetUserNotificationsAsync(int userId, int page = 1, int pageSize = 20, CancellationToken cancellationToken = default);
    Task<int> GetUnreadCountAsync(int userId, CancellationToken cancellationToken = default);
    Task MarkAsReadAsync(int notificationId, int userId, CancellationToken cancellationToken = default);
    Task MarkAllAsReadAsync(int userId, CancellationToken cancellationToken = default);
    Task CreateNotificationAsync(int userId, NotificationType type, string subject, string body, CancellationToken cancellationToken = default);
    Task SendAssignmentNotificationAsync(int assignmentId, CancellationToken cancellationToken = default);
    Task SendReminderNotificationsAsync(CancellationToken cancellationToken = default);
    Task SendPenaltyRiskNotificationAsync(int obligationId, CancellationToken cancellationToken = default);
}