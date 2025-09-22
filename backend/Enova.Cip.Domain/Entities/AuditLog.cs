using Enova.Cip.Domain.Common;

namespace Enova.Cip.Domain.Entities;

public class AuditLog : BaseEntity
{
    public int? ActorId { get; set; }
    public string Action { get; set; } = string.Empty;
    public string EntityType { get; set; } = string.Empty;
    public int? EntityId { get; set; }
    public string? PayloadJson { get; set; }
    public string? IpAddress { get; set; }

    // Navigation properties
    public virtual User? Actor { get; set; }
}