using Microsoft.Extensions.Logging;
using AutoMapper;
using System.Text.Json;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Application.Services;

public class AuditService : IAuditService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IMapper _mapper;
    private readonly ILogger<AuditService> _logger;

    public AuditService(IUnitOfWork unitOfWork, IMapper mapper, ILogger<AuditService> logger)
    {
        _unitOfWork = unitOfWork;
        _mapper = mapper;
        _logger = logger;
    }

    public async Task LogAsync(int? actorId, string action, string entityType, int? entityId, object? payload = null, string? ipAddress = null, CancellationToken cancellationToken = default)
    {
        try
        {
            var auditLog = new AuditLog
            {
                ActorId = actorId,
                Action = action,
                EntityType = entityType,
                EntityId = entityId,
                PayloadJson = payload != null ? JsonSerializer.Serialize(payload) : null,
                IpAddress = ipAddress,
                CreatedAt = DateTime.UtcNow
            };

            await _unitOfWork.AuditLogs.AddAsync(auditLog, cancellationToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            _logger.LogInformation("Audit log created: {Action} on {EntityType} {EntityId} by {ActorId}", action, entityType, entityId, actorId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create audit log for {Action} on {EntityType} {EntityId}", action, entityType, entityId);
        }
    }

    public async Task<IEnumerable<AuditLogDto>> GetAuditLogsAsync(int page = 1, int pageSize = 20, string? entityType = null, int? entityId = null, CancellationToken cancellationToken = default)
    {
        var skip = (page - 1) * pageSize;

        var auditLogs = await _unitOfWork.AuditLogs.FindAsync(
            al => (entityType == null || al.EntityType == entityType) &&
                  (entityId == null || al.EntityId == entityId),
            cancellationToken);

        var orderedLogs = auditLogs
            .OrderByDescending(al => al.CreatedAt)
            .Skip(skip)
            .Take(pageSize)
            .ToList();

        return _mapper.Map<IEnumerable<AuditLogDto>>(orderedLogs);
    }

    public async Task<IEnumerable<AuditLogDto>> GetEntityAuditLogsAsync(string entityType, int entityId, CancellationToken cancellationToken = default)
    {
        var auditLogs = await _unitOfWork.AuditLogs.FindAsync(
            al => al.EntityType == entityType && al.EntityId == entityId,
            cancellationToken);

        var orderedLogs = auditLogs.OrderByDescending(al => al.CreatedAt).ToList();

        return _mapper.Map<IEnumerable<AuditLogDto>>(orderedLogs);
    }
}