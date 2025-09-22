using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class MetadataField : AuditableEntity
{
    public int ContractId { get; set; }
    public string Key { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public DataSource Source { get; set; }
    public double? Confidence { get; set; }
    public string? OffsetsJson { get; set; }

    // Navigation properties
    public virtual Contract Contract { get; set; } = null!;
}