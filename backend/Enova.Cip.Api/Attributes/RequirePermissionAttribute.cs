using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System.Security.Claims;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Api.Attributes;

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class RequirePermissionAttribute : Attribute, IAsyncAuthorizationFilter
{
    private readonly AccessLevel _minimumAccessLevel;

    public RequirePermissionAttribute(AccessLevel minimumAccessLevel = AccessLevel.Viewer)
    {
        _minimumAccessLevel = minimumAccessLevel;
    }

    public async Task OnAuthorizationAsync(AuthorizationFilterContext context)
    {
        // Skip authorization if action is decorated with [AllowAnonymous]
        if (context.ActionDescriptor.EndpointMetadata.Any(x => x.GetType() == typeof(Microsoft.AspNetCore.Authorization.AllowAnonymousAttribute)))
        {
            return;
        }

        var user = context.HttpContext.User;
        if (!user.Identity?.IsAuthenticated ?? true)
        {
            context.Result = new UnauthorizedResult();
            return;
        }

        // Get user ID
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier);
        if (userIdClaim == null || !int.TryParse(userIdClaim.Value, out var userId))
        {
            context.Result = new UnauthorizedResult();
            return;
        }

        // Check if user is Admin (admins have access to everything)
        var roleClaim = user.FindFirst(ClaimTypes.Role);
        if (roleClaim?.Value == UserRole.Admin.ToString())
        {
            return;
        }

        // Get project ID from route
        var projectIdValue = context.RouteData.Values["projectId"]?.ToString() ??
                           context.HttpContext.Request.Query["projectId"].FirstOrDefault() ??
                           context.HttpContext.Request.Headers["X-Project-Id"].FirstOrDefault();

        if (string.IsNullOrEmpty(projectIdValue) || !int.TryParse(projectIdValue, out var projectId))
        {
            // If no project ID is provided, check if the user is trying to access a project-specific resource
            // In some cases, we might need to extract project ID from the resource itself
            var contractIdValue = context.RouteData.Values["contractId"]?.ToString();
            if (!string.IsNullOrEmpty(contractIdValue) && int.TryParse(contractIdValue, out var contractId))
            {
                // Need to resolve project ID from contract ID
                var serviceProvider = context.HttpContext.RequestServices;
                var contractService = serviceProvider.GetRequiredService<IContractService>();

                try
                {
                    var contract = await contractService.GetContractAsync(contractId, userId);
                    if (contract == null)
                    {
                        context.Result = new NotFoundResult();
                        return;
                    }
                    projectId = contract.ProjectId;
                }
                catch
                {
                    context.Result = new ForbidResult();
                    return;
                }
            }
            else
            {
                // For non-project-specific endpoints, allow access
                return;
            }
        }

        // Check permissions
        var serviceProvider = context.HttpContext.RequestServices;
        var projectService = serviceProvider.GetRequiredService<IProjectService>();

        try
        {
            var hasAccess = await projectService.HasAccessAsync(projectId, userId, _minimumAccessLevel);
            if (!hasAccess)
            {
                context.Result = new ForbidResult();
                return;
            }
        }
        catch
        {
            context.Result = new ForbidResult();
            return;
        }
    }
}