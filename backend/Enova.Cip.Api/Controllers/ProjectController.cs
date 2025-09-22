using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using FluentValidation;
using System.Security.Claims;
using Enova.Cip.Api.Attributes;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ProjectController : ControllerBase
{
    private readonly IProjectService _projectService;
    private readonly IValidator<CreateProjectDto> _createValidator;
    private readonly IValidator<UpdateProjectDto> _updateValidator;
    private readonly ILogger<ProjectController> _logger;

    public ProjectController(
        IProjectService projectService,
        IValidator<CreateProjectDto> createValidator,
        IValidator<UpdateProjectDto> updateValidator,
        ILogger<ProjectController> logger)
    {
        _projectService = projectService;
        _createValidator = createValidator;
        _updateValidator = updateValidator;
        _logger = logger;
    }

    /// <summary>
    /// Get all projects accessible to the current user
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<IEnumerable<ProjectDto>>> GetProjects()
    {
        var userId = GetCurrentUserId();
        var projects = await _projectService.GetUserProjectsAsync(userId);
        return Ok(projects);
    }

    /// <summary>
    /// Get a specific project by ID
    /// </summary>
    [HttpGet("{projectId}")]
    [RequirePermission(AccessLevel.Viewer)]
    public async Task<ActionResult<ProjectDto>> GetProject(int projectId)
    {
        var userId = GetCurrentUserId();
        var project = await _projectService.GetProjectAsync(projectId, userId);

        if (project == null)
        {
            return NotFound();
        }

        return Ok(project);
    }

    /// <summary>
    /// Create a new project
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<ProjectDto>> CreateProject([FromBody] CreateProjectDto createProjectDto)
    {
        var validationResult = await _createValidator.ValidateAsync(createProjectDto);
        if (!validationResult.IsValid)
        {
            return BadRequest(validationResult.Errors);
        }

        var userId = GetCurrentUserId();
        var project = await _projectService.CreateProjectAsync(createProjectDto, userId);

        return CreatedAtAction(nameof(GetProject), new { projectId = project.Id }, project);
    }

    /// <summary>
    /// Update an existing project
    /// </summary>
    [HttpPut("{projectId}")]
    [RequirePermission(AccessLevel.Manager)]
    public async Task<ActionResult<ProjectDto>> UpdateProject(int projectId, [FromBody] UpdateProjectDto updateProjectDto)
    {
        var validationResult = await _updateValidator.ValidateAsync(updateProjectDto);
        if (!validationResult.IsValid)
        {
            return BadRequest(validationResult.Errors);
        }

        var userId = GetCurrentUserId();

        try
        {
            var project = await _projectService.UpdateProjectAsync(projectId, updateProjectDto, userId);
            return Ok(project);
        }
        catch (ArgumentException)
        {
            return NotFound();
        }
    }

    /// <summary>
    /// Delete a project
    /// </summary>
    [HttpDelete("{projectId}")]
    [RequirePermission(AccessLevel.Owner)]
    public async Task<IActionResult> DeleteProject(int projectId)
    {
        var userId = GetCurrentUserId();

        try
        {
            await _projectService.DeleteProjectAsync(projectId, userId);
            return NoContent();
        }
        catch (ArgumentException)
        {
            return NotFound();
        }
    }

    /// <summary>
    /// Grant permission to a user for a project
    /// </summary>
    [HttpPost("{projectId}/permissions")]
    [RequirePermission(AccessLevel.Manager)]
    public async Task<ActionResult<UserProjectPermissionDto>> GrantPermission(int projectId, [FromBody] GrantPermissionDto grantPermissionDto)
    {
        var userId = GetCurrentUserId();

        try
        {
            var permission = await _projectService.GrantPermissionAsync(projectId, grantPermissionDto, userId);
            return Ok(permission);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    /// <summary>
    /// Revoke permission from a user for a project
    /// </summary>
    [HttpDelete("{projectId}/permissions/{userId}")]
    [RequirePermission(AccessLevel.Manager)]
    public async Task<IActionResult> RevokePermission(int projectId, int userId)
    {
        var revokedBy = GetCurrentUserId();

        try
        {
            await _projectService.RevokePermissionAsync(projectId, userId, revokedBy);
            return NoContent();
        }
        catch (ArgumentException)
        {
            return NotFound();
        }
    }

    /// <summary>
    /// Get user's access level for a project
    /// </summary>
    [HttpGet("{projectId}/access-level")]
    [RequirePermission(AccessLevel.Viewer)]
    public async Task<ActionResult<object>> GetAccessLevel(int projectId)
    {
        var userId = GetCurrentUserId();
        var accessLevel = await _projectService.GetUserAccessLevelAsync(projectId, userId);

        if (accessLevel == null)
        {
            return NotFound();
        }

        return Ok(new { accessLevel = accessLevel.ToString() });
    }

    private int GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier);
        if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out var userId))
        {
            throw new UnauthorizedAccessException("User ID not found in token");
        }
        return userId;
    }
}