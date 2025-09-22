using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Enova.Cip.Api.Attributes;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class DashboardController : ControllerBase
{
    private readonly IDashboardService _dashboardService;
    private readonly ILogger<DashboardController> _logger;

    public DashboardController(IDashboardService dashboardService, ILogger<DashboardController> logger)
    {
        _dashboardService = dashboardService;
        _logger = logger;
    }

    /// <summary>
    /// Get dashboard statistics for the current user
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<DashboardStatsDto>> GetDashboardStats()
    {
        var userId = GetCurrentUserId();
        var stats = await _dashboardService.GetDashboardStatsAsync(userId);
        return Ok(stats);
    }

    /// <summary>
    /// Get admin dashboard statistics (admin only)
    /// </summary>
    [HttpGet("admin")]
    [RequireRole(UserRole.Admin)]
    public async Task<ActionResult<DashboardStatsDto>> GetAdminDashboardStats()
    {
        var stats = await _dashboardService.GetAdminDashboardStatsAsync();
        return Ok(stats);
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