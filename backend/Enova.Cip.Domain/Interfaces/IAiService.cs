namespace Enova.Cip.Domain.Interfaces;

public class ExtractedMetadata
{
    public string Key { get; set; } = string.Empty;
    public string Value { get; set; } = string.Empty;
    public double Confidence { get; set; }
    public string? OffsetsJson { get; set; }
}

public class ExtractedObligation
{
    public string Description { get; set; } = string.Empty;
    public string? Frequency { get; set; }
    public DateTime? DueDate { get; set; }
    public string? PenaltyText { get; set; }
    public double Confidence { get; set; }
}

public class ContractExtractionResult
{
    public List<ExtractedMetadata> Metadata { get; set; } = new();
    public List<ExtractedObligation> Obligations { get; set; } = new();
}

public interface IAiService
{
    Task<ContractExtractionResult> ExtractContractDataAsync(string fileContent, CancellationToken cancellationToken = default);
    Task<ContractExtractionResult> ExtractContractDataFromFileAsync(Stream fileStream, string fileName, CancellationToken cancellationToken = default);
}