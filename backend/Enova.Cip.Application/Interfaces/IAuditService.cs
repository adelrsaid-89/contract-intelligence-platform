using Enova.Cip.Application.DTOs;

namespace Enova.Cip.Application.Interfaces;

public interface IAuditService
{
    Task LogAsync(int? actorId, string action, string entityType, int? entityId, object? payload = null, string? ipAddress = null, CancellationToken cancellationToken = default);
    Task<IEnumerable<AuditLogDto>> GetAuditLogsAsync(int page = 1, int pageSize = 20, string? entityType = null, int? entityId = null, CancellationToken cancellationToken = default);
    Task<IEnumerable<AuditLogDto>> GetEntityAuditLogsAsync(string entityType, int entityId, CancellationToken cancellationToken = default);
}

public interface IDashboardService
{
    Task<DashboardStatsDto> GetDashboardStatsAsync(int userId, CancellationToken cancellationToken = default);
    Task<DashboardStatsDto> GetAdminDashboardStatsAsync(CancellationToken cancellationToken = default);
}