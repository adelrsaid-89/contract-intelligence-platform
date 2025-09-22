namespace Enova.Cip.Domain.Common;

public abstract class BaseEntity
{
    public int Id { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public abstract class AuditableEntity : BaseEntity
{
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}