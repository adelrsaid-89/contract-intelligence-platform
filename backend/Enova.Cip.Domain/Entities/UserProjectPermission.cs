using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class UserProjectPermission : BaseEntity
{
    public int UserId { get; set; }
    public int ProjectId { get; set; }
    public AccessLevel AccessLevel { get; set; }
    public DateTime GrantedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    public virtual User User { get; set; } = null!;
    public virtual Project Project { get; set; } = null!;
}