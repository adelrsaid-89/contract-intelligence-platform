using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Application.DTOs;

public class ProjectDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public ProjectStatus Status { get; set; }
    public string ClientName { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public List<UserProjectPermissionDto> UserPermissions { get; set; } = new();
    public int ContractCount { get; set; }
}

public class CreateProjectDto
{
    public string Name { get; set; } = string.Empty;
    public string ClientName { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;
}

public class UpdateProjectDto
{
    public string Name { get; set; } = string.Empty;
    public ProjectStatus Status { get; set; }
    public string ClientName { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;
}

public class UserProjectPermissionDto
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public int ProjectId { get; set; }
    public AccessLevel AccessLevel { get; set; }
    public DateTime GrantedAt { get; set; }
    public UserDto? User { get; set; }
}

public class GrantPermissionDto
{
    public int UserId { get; set; }
    public AccessLevel AccessLevel { get; set; }
}