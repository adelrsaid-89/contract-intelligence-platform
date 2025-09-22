using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class Project : AuditableEntity
{
    public string Name { get; set; } = string.Empty;
    public ProjectStatus Status { get; set; } = ProjectStatus.Active;
    public string ClientName { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;

    // Navigation properties
    public virtual ICollection<UserProjectPermission> UserPermissions { get; set; } = new List<UserProjectPermission>();
    public virtual ICollection<Contract> Contracts { get; set; } = new List<Contract>();
}