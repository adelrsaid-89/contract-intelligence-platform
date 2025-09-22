using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class Notification : BaseEntity
{
    public int UserId { get; set; }
    public NotificationType Type { get; set; }
    public string Subject { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public DateTime? SentAt { get; set; }
    public NotificationStatus Status { get; set; } = NotificationStatus.Pending;
    public DateTime? ReadAt { get; set; }

    // Navigation properties
    public virtual User User { get; set; } = null!;
}