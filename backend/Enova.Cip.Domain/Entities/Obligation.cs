using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class Obligation : AuditableEntity
{
    public int ContractId { get; set; }
    public string Description { get; set; } = string.Empty;
    public string? Frequency { get; set; }
    public DateTime? DueDate { get; set; }
    public string? PenaltyText { get; set; }
    public DataSource Source { get; set; }
    public double? Confidence { get; set; }

    // Navigation properties
    public virtual Contract Contract { get; set; } = null!;
    public virtual ICollection<Assignment> Assignments { get; set; } = new List<Assignment>();
    public virtual ICollection<PenaltyRisk> PenaltyRisks { get; set; } = new List<PenaltyRisk>();
}