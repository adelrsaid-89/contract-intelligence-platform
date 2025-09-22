using Enova.Cip.Domain.Common;

namespace Enova.Cip.Domain.Entities;

public class PenaltyRisk : BaseEntity
{
    public int ObligationId { get; set; }
    public DateTime ComputedAt { get; set; } = DateTime.UtcNow;
    public double RiskScore { get; set; }
    public string Basis { get; set; } = string.Empty;
    public decimal? Amount { get; set; }

    // Navigation properties
    public virtual Obligation Obligation { get; set; } = null!;
}