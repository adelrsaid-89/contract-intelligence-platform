using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.DTOs;

public class ObligationDto
{
    public int Id { get; set; }
    public int ContractId { get; set; }
    public string Description { get; set; } = string.Empty;
    public string? Frequency { get; set; }
    public DateTime? DueDate { get; set; }
    public string? PenaltyText { get; set; }
    public DataSource Source { get; set; }
    public double? Confidence { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public ContractDto? Contract { get; set; }
    public List<AssignmentDto> Assignments { get; set; } = new();
    public List<PenaltyRiskDto> PenaltyRisks { get; set; } = new();
}

public class CreateObligationDto
{
    public int ContractId { get; set; }
    public string Description { get; set; } = string.Empty;
    public string? Frequency { get; set; }
    public DateTime? DueDate { get; set; }
    public string? PenaltyText { get; set; }
}

public class UpdateObligationDto
{
    public string Description { get; set; } = string.Empty;
    public string? Frequency { get; set; }
    public DateTime? DueDate { get; set; }
    public string? PenaltyText { get; set; }
}

public class AssignmentDto
{
    public int Id { get; set; }
    public int ObligationId { get; set; }
    public int AssigneeUserId { get; set; }
    public AssignmentStatus Status { get; set; }
    public int PercentComplete { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public ObligationDto? Obligation { get; set; }
    public UserDto? AssigneeUser { get; set; }
    public List<EvidenceDto> Evidence { get; set; } = new();
}

public class CreateAssignmentDto
{
    public int ObligationId { get; set; }
    public int AssigneeUserId { get; set; }
}

public class UpdateAssignmentDto
{
    public AssignmentStatus Status { get; set; }
    public int PercentComplete { get; set; }
}

public class EvidenceDto
{
    public int Id { get; set; }
    public int AssignmentId { get; set; }
    public string ObjectKey { get; set; } = string.Empty;
    public int UploadedBy { get; set; }
    public DateTime UploadedAt { get; set; }
    public string? Note { get; set; }
    public long FileSize { get; set; }
    public string OriginalFileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public UserDto? UploadedByUser { get; set; }
    public string? DownloadUrl { get; set; }
}

public class PenaltyRiskDto
{
    public int Id { get; set; }
    public int ObligationId { get; set; }
    public DateTime ComputedAt { get; set; }
    public double RiskScore { get; set; }
    public string Basis { get; set; } = string.Empty;
    public decimal? Amount { get; set; }
}