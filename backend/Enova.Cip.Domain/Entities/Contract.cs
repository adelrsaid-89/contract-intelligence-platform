using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class Contract : AuditableEntity
{
    public int ProjectId { get; set; }
    public string Title { get; set; } = string.Empty;
    public decimal? ContractValue { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string PaymentTerms { get; set; } = string.Empty;
    public ContractStatus Status { get; set; } = ContractStatus.Draft;

    // Navigation properties
    public virtual Project Project { get; set; } = null!;
    public virtual ICollection<ContractFile> Files { get; set; } = new List<ContractFile>();
    public virtual ICollection<MetadataField> MetadataFields { get; set; } = new List<MetadataField>();
    public virtual ICollection<Obligation> Obligations { get; set; } = new List<Obligation>();
}