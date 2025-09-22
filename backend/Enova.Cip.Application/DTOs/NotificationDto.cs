using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.DTOs;

public class NotificationDto
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public NotificationType Type { get; set; }
    public string Subject { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public DateTime? SentAt { get; set; }
    public NotificationStatus Status { get; set; }
    public DateTime? ReadAt { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class AuditLogDto
{
    public int Id { get; set; }
    public int? ActorId { get; set; }
    public string Action { get; set; } = string.Empty;
    public string EntityType { get; set; } = string.Empty;
    public int? EntityId { get; set; }
    public string? PayloadJson { get; set; }
    public DateTime CreatedAt { get; set; }
    public string? IpAddress { get; set; }
    public UserDto? Actor { get; set; }
}

public class DashboardStatsDto
{
    public int TotalProjects { get; set; }
    public int ActiveProjects { get; set; }
    public int TotalContracts { get; set; }
    public int ActiveContracts { get; set; }
    public int TotalObligations { get; set; }
    public int OverdueAssignments { get; set; }
    public int PendingAssignments { get; set; }
    public int CompletedAssignments { get; set; }
    public List<AssignmentDto> RecentAssignments { get; set; } = new();
    public List<ObligationDto> UpcomingObligations { get; set; } = new();
    public List<PenaltyRiskDto> HighRiskObligations { get; set; } = new();
}