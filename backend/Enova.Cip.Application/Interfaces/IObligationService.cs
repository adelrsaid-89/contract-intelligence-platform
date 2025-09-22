using Enova.Cip.Application.DTOs;

namespace Enova.Cip.Application.Interfaces;

public interface IObligationService
{
    Task<IEnumerable<ObligationDto>> GetContractObligationsAsync(int contractId, int userId, CancellationToken cancellationToken = default);
    Task<ObligationDto?> GetObligationAsync(int obligationId, int userId, CancellationToken cancellationToken = default);
    Task<ObligationDto> CreateObligationAsync(CreateObligationDto createObligationDto, int createdBy, CancellationToken cancellationToken = default);
    Task<ObligationDto> UpdateObligationAsync(int obligationId, UpdateObligationDto updateObligationDto, int userId, CancellationToken cancellationToken = default);
    Task DeleteObligationAsync(int obligationId, int userId, CancellationToken cancellationToken = default);
    Task<AssignmentDto> AssignObligationAsync(int obligationId, CreateAssignmentDto createAssignmentDto, int assignedBy, CancellationToken cancellationToken = default);
    Task<AssignmentDto> UpdateAssignmentAsync(int assignmentId, UpdateAssignmentDto updateAssignmentDto, int userId, CancellationToken cancellationToken = default);
    Task<EvidenceDto> UploadEvidenceAsync(int assignmentId, Stream fileStream, string fileName, string contentType, string? note, int uploadedBy, CancellationToken cancellationToken = default);
    Task<IEnumerable<AssignmentDto>> GetUserAssignmentsAsync(int userId, CancellationToken cancellationToken = default);
    Task<IEnumerable<ObligationDto>> GetUpcomingObligationsAsync(int userId, int days = 30, CancellationToken cancellationToken = default);
}