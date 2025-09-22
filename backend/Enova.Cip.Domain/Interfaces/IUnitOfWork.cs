using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Domain.Interfaces;

public interface IUnitOfWork : IDisposable
{
    IRepository<User> Users { get; }
    IRepository<Project> Projects { get; }
    IRepository<UserProjectPermission> UserProjectPermissions { get; }
    IRepository<Contract> Contracts { get; }
    IRepository<ContractFile> ContractFiles { get; }
    IRepository<MetadataField> MetadataFields { get; }
    IRepository<Obligation> Obligations { get; }
    IRepository<Assignment> Assignments { get; }
    IRepository<Evidence> Evidence { get; }
    IRepository<Notification> Notifications { get; }
    IRepository<PenaltyRisk> PenaltyRisks { get; }
    IRepository<AuditLog> AuditLogs { get; }

    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
    Task BeginTransactionAsync(CancellationToken cancellationToken = default);
    Task CommitTransactionAsync(CancellationToken cancellationToken = default);
    Task RollbackTransactionAsync(CancellationToken cancellationToken = default);
}