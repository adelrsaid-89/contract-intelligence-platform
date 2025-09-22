using Microsoft.Extensions.Logging;
using AutoMapper;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Application.Services;

public class ProjectService : IProjectService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IMapper _mapper;
    private readonly IAuditService _auditService;
    private readonly ILogger<ProjectService> _logger;

    public ProjectService(IUnitOfWork unitOfWork, IMapper mapper, IAuditService auditService, ILogger<ProjectService> logger)
    {
        _unitOfWork = unitOfWork;
        _mapper = mapper;
        _auditService = auditService;
        _logger = logger;
    }

    public async Task<IEnumerable<ProjectDto>> GetUserProjectsAsync(int userId, CancellationToken cancellationToken = default)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(userId, cancellationToken);
        if (user == null)
        {
            throw new UnauthorizedAccessException("User not found");
        }

        // Admin can see all projects, others only see their assigned projects
        IEnumerable<Project> projects;
        if (user.Role == UserRole.Admin)
        {
            projects = await _unitOfWork.Projects.GetAllAsync(cancellationToken);
        }
        else
        {
            var permissions = await _unitOfWork.UserProjectPermissions.FindAsync(
                up => up.UserId == userId, cancellationToken);
            var projectIds = permissions.Select(p => p.ProjectId);
            projects = await _unitOfWork.Projects.FindAsync(
                p => projectIds.Contains(p.Id), cancellationToken);
        }

        var projectDtos = _mapper.Map<IEnumerable<ProjectDto>>(projects);

        // Add contract counts and permissions
        foreach (var projectDto in projectDtos)
        {
            var contractCount = await _unitOfWork.Contracts.CountAsync(
                c => c.ProjectId == projectDto.Id, cancellationToken);
            projectDto.ContractCount = contractCount;

            var permissions = await _unitOfWork.UserProjectPermissions.FindAsync(
                up => up.ProjectId == projectDto.Id, cancellationToken);
            projectDto.UserPermissions = _mapper.Map<List<UserProjectPermissionDto>>(permissions);
        }

        return projectDtos;
    }

    public async Task<ProjectDto?> GetProjectAsync(int projectId, int userId, CancellationToken cancellationToken = default)
    {
        if (!await HasAccessAsync(projectId, userId, AccessLevel.Viewer, cancellationToken))
        {
            throw new UnauthorizedAccessException("Access denied to project");
        }

        var project = await _unitOfWork.Projects.GetByIdAsync(projectId, cancellationToken);
        if (project == null)
        {
            return null;
        }

        var projectDto = _mapper.Map<ProjectDto>(project);

        var contractCount = await _unitOfWork.Contracts.CountAsync(
            c => c.ProjectId == projectId, cancellationToken);
        projectDto.ContractCount = contractCount;

        var permissions = await _unitOfWork.UserProjectPermissions.FindAsync(
            up => up.ProjectId == projectId, cancellationToken);
        projectDto.UserPermissions = _mapper.Map<List<UserProjectPermissionDto>>(permissions);

        return projectDto;
    }

    public async Task<ProjectDto> CreateProjectAsync(CreateProjectDto createProjectDto, int createdBy, CancellationToken cancellationToken = default)
    {
        var project = _mapper.Map<Project>(createProjectDto);
        project.CreatedAt = DateTime.UtcNow;
        project.UpdatedAt = DateTime.UtcNow;

        await _unitOfWork.Projects.AddAsync(project, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        // Grant owner permission to creator
        var permission = new UserProjectPermission
        {
            UserId = createdBy,
            ProjectId = project.Id,
            AccessLevel = AccessLevel.Owner,
            GrantedAt = DateTime.UtcNow
        };

        await _unitOfWork.UserProjectPermissions.AddAsync(permission, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        await _auditService.LogAsync(createdBy, "CREATE", "Project", project.Id, createProjectDto, cancellationToken: cancellationToken);

        return _mapper.Map<ProjectDto>(project);
    }

    public async Task<ProjectDto> UpdateProjectAsync(int projectId, UpdateProjectDto updateProjectDto, int userId, CancellationToken cancellationToken = default)
    {
        if (!await HasAccessAsync(projectId, userId, AccessLevel.Manager, cancellationToken))
        {
            throw new UnauthorizedAccessException("Access denied to update project");
        }

        var project = await _unitOfWork.Projects.GetByIdAsync(projectId, cancellationToken);
        if (project == null)
        {
            throw new ArgumentException("Project not found");
        }

        _mapper.Map(updateProjectDto, project);
        project.UpdatedAt = DateTime.UtcNow;

        await _unitOfWork.Projects.UpdateAsync(project, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        await _auditService.LogAsync(userId, "UPDATE", "Project", projectId, updateProjectDto, cancellationToken: cancellationToken);

        return _mapper.Map<ProjectDto>(project);
    }

    public async Task DeleteProjectAsync(int projectId, int userId, CancellationToken cancellationToken = default)
    {
        if (!await HasAccessAsync(projectId, userId, AccessLevel.Owner, cancellationToken))
        {
            throw new UnauthorizedAccessException("Access denied to delete project");
        }

        var project = await _unitOfWork.Projects.GetByIdAsync(projectId, cancellationToken);
        if (project == null)
        {
            throw new ArgumentException("Project not found");
        }

        await _unitOfWork.Projects.DeleteAsync(project, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        await _auditService.LogAsync(userId, "DELETE", "Project", projectId, cancellationToken: cancellationToken);
    }

    public async Task<UserProjectPermissionDto> GrantPermissionAsync(int projectId, GrantPermissionDto grantPermissionDto, int grantedBy, CancellationToken cancellationToken = default)
    {
        if (!await HasAccessAsync(projectId, grantedBy, AccessLevel.Manager, cancellationToken))
        {
            throw new UnauthorizedAccessException("Access denied to grant permissions");
        }

        // Check if permission already exists
        var existingPermission = await _unitOfWork.UserProjectPermissions.FindFirstAsync(
            up => up.ProjectId == projectId && up.UserId == grantPermissionDto.UserId, cancellationToken);

        if (existingPermission != null)
        {
            existingPermission.AccessLevel = grantPermissionDto.AccessLevel;
            await _unitOfWork.UserProjectPermissions.UpdateAsync(existingPermission, cancellationToken);
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            await _auditService.LogAsync(grantedBy, "UPDATE_PERMISSION", "UserProjectPermission", existingPermission.Id, grantPermissionDto, cancellationToken: cancellationToken);

            return _mapper.Map<UserProjectPermissionDto>(existingPermission);
        }

        var permission = new UserProjectPermission
        {
            ProjectId = projectId,
            UserId = grantPermissionDto.UserId,
            AccessLevel = grantPermissionDto.AccessLevel,
            GrantedAt = DateTime.UtcNow
        };

        await _unitOfWork.UserProjectPermissions.AddAsync(permission, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        await _auditService.LogAsync(grantedBy, "GRANT_PERMISSION", "UserProjectPermission", permission.Id, grantPermissionDto, cancellationToken: cancellationToken);

        return _mapper.Map<UserProjectPermissionDto>(permission);
    }

    public async Task RevokePermissionAsync(int projectId, int userId, int revokedBy, CancellationToken cancellationToken = default)
    {
        if (!await HasAccessAsync(projectId, revokedBy, AccessLevel.Manager, cancellationToken))
        {
            throw new UnauthorizedAccessException("Access denied to revoke permissions");
        }

        var permission = await _unitOfWork.UserProjectPermissions.FindFirstAsync(
            up => up.ProjectId == projectId && up.UserId == userId, cancellationToken);

        if (permission == null)
        {
            throw new ArgumentException("Permission not found");
        }

        await _unitOfWork.UserProjectPermissions.DeleteAsync(permission, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        await _auditService.LogAsync(revokedBy, "REVOKE_PERMISSION", "UserProjectPermission", permission.Id, cancellationToken: cancellationToken);
    }

    public async Task<AccessLevel?> GetUserAccessLevelAsync(int projectId, int userId, CancellationToken cancellationToken = default)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(userId, cancellationToken);
        if (user == null)
        {
            return null;
        }

        // Admin has owner access to all projects
        if (user.Role == UserRole.Admin)
        {
            return AccessLevel.Owner;
        }

        var permission = await _unitOfWork.UserProjectPermissions.FindFirstAsync(
            up => up.ProjectId == projectId && up.UserId == userId, cancellationToken);

        return permission?.AccessLevel;
    }

    public async Task<bool> HasAccessAsync(int projectId, int userId, AccessLevel minimumLevel = AccessLevel.Viewer, CancellationToken cancellationToken = default)
    {
        var userAccessLevel = await GetUserAccessLevelAsync(projectId, userId, cancellationToken);
        return userAccessLevel.HasValue && userAccessLevel.Value <= minimumLevel;
    }
}