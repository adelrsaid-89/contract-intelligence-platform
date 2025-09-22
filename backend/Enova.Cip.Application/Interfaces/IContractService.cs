using Enova.Cip.Application.DTOs;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.Interfaces;

public interface IContractService
{
    Task<IEnumerable<ContractDto>> GetProjectContractsAsync(int projectId, int userId, CancellationToken cancellationToken = default);
    Task<ContractDto?> GetContractAsync(int contractId, int userId, CancellationToken cancellationToken = default);
    Task<ContractDto> CreateContractAsync(CreateContractDto createContractDto, int createdBy, CancellationToken cancellationToken = default);
    Task<ContractDto> UpdateContractAsync(int contractId, UpdateContractDto updateContractDto, int userId, CancellationToken cancellationToken = default);
    Task DeleteContractAsync(int contractId, int userId, CancellationToken cancellationToken = default);
    Task<ContractFileDto> UploadFileAsync(int contractId, Stream fileStream, string fileName, string contentType, FolderType folderType, int uploadedBy, CancellationToken cancellationToken = default);
    Task<Stream> DownloadFileAsync(int fileId, int userId, CancellationToken cancellationToken = default);
    Task DeleteFileAsync(int fileId, int userId, CancellationToken cancellationToken = default);
    Task ExtractContractDataAsync(int contractId, int userId, CancellationToken cancellationToken = default);
    Task<IEnumerable<MetadataFieldDto>> GetContractMetadataAsync(int contractId, int userId, CancellationToken cancellationToken = default);
    Task UpdateMetadataFieldAsync(int fieldId, string value, int userId, CancellationToken cancellationToken = default);
}