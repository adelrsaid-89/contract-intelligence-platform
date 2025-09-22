using Enova.Cip.Application.DTOs;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.Interfaces;

public interface IProjectService
{
    Task<IEnumerable<ProjectDto>> GetUserProjectsAsync(int userId, CancellationToken cancellationToken = default);
    Task<ProjectDto?> GetProjectAsync(int projectId, int userId, CancellationToken cancellationToken = default);
    Task<ProjectDto> CreateProjectAsync(CreateProjectDto createProjectDto, int createdBy, CancellationToken cancellationToken = default);
    Task<ProjectDto> UpdateProjectAsync(int projectId, UpdateProjectDto updateProjectDto, int userId, CancellationToken cancellationToken = default);
    Task DeleteProjectAsync(int projectId, int userId, CancellationToken cancellationToken = default);
    Task<UserProjectPermissionDto> GrantPermissionAsync(int projectId, GrantPermissionDto grantPermissionDto, int grantedBy, CancellationToken cancellationToken = default);
    Task RevokePermissionAsync(int projectId, int userId, int revokedBy, CancellationToken cancellationToken = default);
    Task<AccessLevel?> GetUserAccessLevelAsync(int projectId, int userId, CancellationToken cancellationToken = default);
    Task<bool> HasAccessAsync(int projectId, int userId, AccessLevel minimumLevel = AccessLevel.Viewer, CancellationToken cancellationToken = default);
}