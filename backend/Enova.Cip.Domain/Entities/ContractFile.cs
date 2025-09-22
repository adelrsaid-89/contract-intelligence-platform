using Enova.Cip.Domain.Common;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Domain.Entities;

public class ContractFile : BaseEntity
{
    public int ContractId { get; set; }
    public FolderType FolderType { get; set; }
    public string ObjectKey { get; set; } = string.Empty;
    public int Version { get; set; } = 1;
    public int UploadedBy { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    public string Hash { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public string OriginalFileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;

    // Navigation properties
    public virtual Contract Contract { get; set; } = null!;
    public virtual User UploadedByUser { get; set; } = null!;
}