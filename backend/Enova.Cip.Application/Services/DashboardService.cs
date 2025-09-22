using Microsoft.Extensions.Logging;
using AutoMapper;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Domain.Enums;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Application.Services;

public class DashboardService : IDashboardService
{
    private readonly IUnitOfWork _unitOfWork;
    private readonly IMapper _mapper;
    private readonly IProjectService _projectService;
    private readonly ILogger<DashboardService> _logger;

    public DashboardService(IUnitOfWork unitOfWork, IMapper mapper, IProjectService projectService, ILogger<DashboardService> logger)
    {
        _unitOfWork = unitOfWork;
        _mapper = mapper;
        _projectService = projectService;
        _logger = logger;
    }

    public async Task<DashboardStatsDto> GetDashboardStatsAsync(int userId, CancellationToken cancellationToken = default)
    {
        var user = await _unitOfWork.Users.GetByIdAsync(userId, cancellationToken);
        if (user == null)
        {
            throw new UnauthorizedAccessException("User not found");
        }

        // Get user's accessible projects
        var userProjects = await _projectService.GetUserProjectsAsync(userId, cancellationToken);
        var projectIds = userProjects.Select(p => p.Id).ToList();

        // Get contracts in user's projects
        var contracts = await _unitOfWork.Contracts.FindAsync(
            c => projectIds.Contains(c.ProjectId), cancellationToken);
        var contractIds = contracts.Select(c => c.Id).ToList();

        // Get obligations in user's contracts
        var obligations = await _unitOfWork.Obligations.FindAsync(
            o => contractIds.Contains(o.ContractId), cancellationToken);
        var obligationIds = obligations.Select(o => o.Id).ToList();

        // Get assignments for the user
        var userAssignments = await _unitOfWork.Assignments.FindAsync(
            a => a.AssigneeUserId == userId, cancellationToken);

        // Get all assignments for user's obligations (for broader view)
        var allAssignments = await _unitOfWork.Assignments.FindAsync(
            a => obligationIds.Contains(a.ObligationId), cancellationToken);

        // Calculate stats
        var stats = new DashboardStatsDto
        {
            TotalProjects = userProjects.Count(),
            ActiveProjects = userProjects.Count(p => p.Status == ProjectStatus.Active),
            TotalContracts = contracts.Count(),
            ActiveContracts = contracts.Count(c => c.Status == ContractStatus.Active),
            TotalObligations = obligations.Count(),
            OverdueAssignments = userAssignments.Count(a => a.Status == AssignmentStatus.Overdue),
            PendingAssignments = userAssignments.Count(a => a.Status == AssignmentStatus.Open || a.Status == AssignmentStatus.InProgress),
            CompletedAssignments = userAssignments.Count(a => a.Status == AssignmentStatus.Done)
        };

        // Get recent assignments
        var recentAssignments = userAssignments
            .OrderByDescending(a => a.CreatedAt)
            .Take(5)
            .ToList();
        stats.RecentAssignments = _mapper.Map<List<AssignmentDto>>(recentAssignments);

        // Get upcoming obligations (next 30 days)
        var upcomingObligations = obligations
            .Where(o => o.DueDate.HasValue && o.DueDate.Value >= DateTime.UtcNow && o.DueDate.Value <= DateTime.UtcNow.AddDays(30))
            .OrderBy(o => o.DueDate)
            .Take(5)
            .ToList();
        stats.UpcomingObligations = _mapper.Map<List<ObligationDto>>(upcomingObligations);

        // Get high-risk obligations
        var penaltyRisks = await _unitOfWork.PenaltyRisks.FindAsync(
            pr => obligationIds.Contains(pr.ObligationId) && pr.RiskScore >= 0.7, cancellationToken);
        var highRiskPenalties = penaltyRisks
            .OrderByDescending(pr => pr.RiskScore)
            .Take(5)
            .ToList();
        stats.HighRiskObligations = _mapper.Map<List<PenaltyRiskDto>>(highRiskPenalties);

        return stats;
    }

    public async Task<DashboardStatsDto> GetAdminDashboardStatsAsync(CancellationToken cancellationToken = default)
    {
        // Get all data for admin view
        var allProjects = await _unitOfWork.Projects.GetAllAsync(cancellationToken);
        var allContracts = await _unitOfWork.Contracts.GetAllAsync(cancellationToken);
        var allObligations = await _unitOfWork.Obligations.GetAllAsync(cancellationToken);
        var allAssignments = await _unitOfWork.Assignments.GetAllAsync(cancellationToken);
        var allPenaltyRisks = await _unitOfWork.PenaltyRisks.GetAllAsync(cancellationToken);

        var stats = new DashboardStatsDto
        {
            TotalProjects = allProjects.Count(),
            ActiveProjects = allProjects.Count(p => p.Status == ProjectStatus.Active),
            TotalContracts = allContracts.Count(),
            ActiveContracts = allContracts.Count(c => c.Status == ContractStatus.Active),
            TotalObligations = allObligations.Count(),
            OverdueAssignments = allAssignments.Count(a => a.Status == AssignmentStatus.Overdue),
            PendingAssignments = allAssignments.Count(a => a.Status == AssignmentStatus.Open || a.Status == AssignmentStatus.InProgress),
            CompletedAssignments = allAssignments.Count(a => a.Status == AssignmentStatus.Done)
        };

        // Get recent assignments across all projects
        var recentAssignments = allAssignments
            .OrderByDescending(a => a.CreatedAt)
            .Take(10)
            .ToList();
        stats.RecentAssignments = _mapper.Map<List<AssignmentDto>>(recentAssignments);

        // Get upcoming obligations (next 30 days)
        var upcomingObligations = allObligations
            .Where(o => o.DueDate.HasValue && o.DueDate.Value >= DateTime.UtcNow && o.DueDate.Value <= DateTime.UtcNow.AddDays(30))
            .OrderBy(o => o.DueDate)
            .Take(10)
            .ToList();
        stats.UpcomingObligations = _mapper.Map<List<ObligationDto>>(upcomingObligations);

        // Get high-risk obligations
        var highRiskPenalties = allPenaltyRisks
            .Where(pr => pr.RiskScore >= 0.7)
            .OrderByDescending(pr => pr.RiskScore)
            .Take(10)
            .ToList();
        stats.HighRiskObligations = _mapper.Map<List<PenaltyRiskDto>>(highRiskPenalties);

        return stats;
    }
}