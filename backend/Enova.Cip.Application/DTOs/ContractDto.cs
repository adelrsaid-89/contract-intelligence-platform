using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.DTOs;

public class ContractDto
{
    public int Id { get; set; }
    public int ProjectId { get; set; }
    public string Title { get; set; } = string.Empty;
    public decimal? ContractValue { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string PaymentTerms { get; set; } = string.Empty;
    public ContractStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public ProjectDto? Project { get; set; }
    public List<ContractFileDto> Files { get; set; } = new();
    public List<MetadataFieldDto> MetadataFields { get; set; } = new();
    public List<ObligationDto> Obligations { get; set; } = new();
}

public class CreateContractDto
{
    public int ProjectId { get; set; }
    public string Title { get; set; } = string.Empty;
    public decimal? ContractValue { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string PaymentTerms { get; set; } = string.Empty;
}

public class UpdateContractDto
{
    public string Title { get; set; } = string.Empty;
    public decimal? ContractValue { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string PaymentTerms { get; set; } = string.Empty;
    public ContractStatus Status { get; set; }
}

public class ContractFileDto
{
    public int Id { get; set; }
    public int ContractId { get; set; }
    public FolderType FolderType { get; set; }
    public string ObjectKey { get; set; } = string.Empty;
    public int Version { get; set; }
    public int UploadedBy { get; set; }
    public DateTime UploadedAt { get; set; }
    public string Hash { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public string OriginalFileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public UserDto? UploadedByUser { get; set; }
    public string? DownloadUrl { get; set; }
}

public class MetadataFieldDto
{
    public int Id { get; set; }
    public int ContractId { get; set; }
    public string Key { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public DataSource Source { get; set; }
    public double? Confidence { get; set; }
    public string? OffsetsJson { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}