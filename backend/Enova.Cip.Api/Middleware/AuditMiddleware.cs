using System.Security.Claims;
using Enova.Cip.Application.Interfaces;

namespace Enova.Cip.Api.Middleware;

public class AuditMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AuditMiddleware> _logger;

    public AuditMiddleware(RequestDelegate next, ILogger<AuditMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, IAuditService auditService)
    {
        await _next(context);

        // Only audit state-changing operations
        if (IsStateChangingRequest(context.Request.Method))
        {
            try
            {
                var userId = GetUserId(context.User);
                var ipAddress = GetClientIpAddress(context);
                var path = context.Request.Path.Value ?? "";
                var method = context.Request.Method;
                var statusCode = context.Response.StatusCode;

                // Only log successful operations
                if (statusCode >= 200 && statusCode < 300)
                {
                    var action = $"{method} {path}";
                    await auditService.LogAsync(
                        userId,
                        action,
                        "HttpRequest",
                        null,
                        new { Method = method, Path = path, StatusCode = statusCode },
                        ipAddress);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create audit log for request");
            }
        }
    }

    private static bool IsStateChangingRequest(string method)
    {
        return method switch
        {
            "POST" or "PUT" or "PATCH" or "DELETE" => true,
            _ => false
        };
    }

    private static int? GetUserId(ClaimsPrincipal user)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier);
        return userIdClaim != null && int.TryParse(userIdClaim.Value, out var userId) ? userId : null;
    }

    private static string? GetClientIpAddress(HttpContext context)
    {
        return context.Connection.RemoteIpAddress?.ToString();
    }
}