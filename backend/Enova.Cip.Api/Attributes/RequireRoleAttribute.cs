using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System.Security.Claims;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Api.Attributes;

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class RequireRoleAttribute : Attribute, IAuthorizationFilter
{
    private readonly UserRole[] _allowedRoles;

    public RequireRoleAttribute(params UserRole[] allowedRoles)
    {
        _allowedRoles = allowedRoles;
    }

    public void OnAuthorization(AuthorizationFilterContext context)
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

        var roleClaim = user.FindFirst(ClaimTypes.Role);
        if (roleClaim == null || !Enum.TryParse<UserRole>(roleClaim.Value, out var userRole))
        {
            context.Result = new UnauthorizedResult();
            return;
        }

        if (!_allowedRoles.Contains(userRole))
        {
            context.Result = new ForbidResult();
            return;
        }
    }
}