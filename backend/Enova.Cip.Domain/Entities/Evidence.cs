using Enova.Cip.Domain.Common;

namespace Enova.Cip.Domain.Entities;

public class Evidence : BaseEntity
{
    public int AssignmentId { get; set; }
    public string ObjectKey { get; set; } = string.Empty;
    public int UploadedBy { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    public string? Note { get; set; }
    public long FileSize { get; set; }
    public string OriginalFileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;

    // Navigation properties
    public virtual Assignment Assignment { get; set; } = null!;
    public virtual User UploadedByUser { get; set; } = null!;
}