using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class Assignment : AuditableEntity
{
    public int ObligationId { get; set; }
    public int AssigneeUserId { get; set; }
    public AssignmentStatus Status { get; set; } = AssignmentStatus.Open;
    public int PercentComplete { get; set; } = 0;

    // Navigation properties
    public virtual Obligation Obligation { get; set; } = null!;
    public virtual User AssigneeUser { get; set; } = null!;
    public virtual ICollection<Evidence> Evidence { get; set; } = new List<Evidence>();
}