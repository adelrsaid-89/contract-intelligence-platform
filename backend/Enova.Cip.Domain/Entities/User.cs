using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class User : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public UserRole Role { get; set; }
    public string PasswordHash { get; set; } = string.Empty;
    public bool IsActive { get; set; } = true;

    // Navigation properties
    public virtual ICollection<UserProjectPermission> ProjectPermissions { get; set; } = new List<UserProjectPermission>();
    public virtual ICollection<Assignment> Assignments { get; set; } = new List<Assignment>();
    public virtual ICollection<ContractFile> UploadedFiles { get; set; } = new List<ContractFile>();
    public virtual ICollection<Evidence> UploadedEvidence { get; set; } = new List<Evidence>();
    public virtual ICollection<Notification> Notifications { get; set; } = new List<Notification>();
    public virtual ICollection<AuditLog> AuditLogs { get; set; } = new List<AuditLog>();
}