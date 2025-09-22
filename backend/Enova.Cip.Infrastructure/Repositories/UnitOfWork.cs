using Microsoft.EntityFrameworkCore.Storage;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Interfaces;
using Enova.Cip.Infrastructure.Data;

namespace Enova.Cip.Infrastructure.Repositories;

public class UnitOfWork : IUnitOfWork
{
    private readonly CipDbContext _context;
    private IDbContextTransaction? _transaction;
    private bool _disposed = false;

    private IRepository<User>? _users;
    private IRepository<Project>? _projects;
    private IRepository<UserProjectPermission>? _userProjectPermissions;
    private IRepository<Contract>? _contracts;
    private IRepository<ContractFile>? _contractFiles;
    private IRepository<MetadataField>? _metadataFields;
    private IRepository<Obligation>? _obligations;
    private IRepository<Assignment>? _assignments;
    private IRepository<Evidence>? _evidence;
    private IRepository<Notification>? _notifications;
    private IRepository<PenaltyRisk>? _penaltyRisks;
    private IRepository<AuditLog>? _auditLogs;

    public UnitOfWork(CipDbContext context)
    {
        _context = context;
    }

    public IRepository<User> Users => _users ??= new Repository<User>(_context);
    public IRepository<Project> Projects => _projects ??= new Repository<Project>(_context);
    public IRepository<UserProjectPermission> UserProjectPermissions => _userProjectPermissions ??= new Repository<UserProjectPermission>(_context);
    public IRepository<Contract> Contracts => _contracts ??= new Repository<Contract>(_context);
    public IRepository<ContractFile> ContractFiles => _contractFiles ??= new Repository<ContractFile>(_context);
    public IRepository<MetadataField> MetadataFields => _metadataFields ??= new Repository<MetadataField>(_context);
    public IRepository<Obligation> Obligations => _obligations ??= new Repository<Obligation>(_context);
    public IRepository<Assignment> Assignments => _assignments ??= new Repository<Assignment>(_context);
    public IRepository<Evidence> Evidence => _evidence ??= new Repository<Evidence>(_context);
    public IRepository<Notification> Notifications => _notifications ??= new Repository<Notification>(_context);
    public IRepository<PenaltyRisk> PenaltyRisks => _penaltyRisks ??= new Repository<PenaltyRisk>(_context);
    public IRepository<AuditLog> AuditLogs => _auditLogs ??= new Repository<AuditLog>(_context);

    public async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        return await _context.SaveChangesAsync(cancellationToken);
    }

    public async Task BeginTransactionAsync(CancellationToken cancellationToken = default)
    {
        _transaction = await _context.Database.BeginTransactionAsync(cancellationToken);
    }

    public async Task CommitTransactionAsync(CancellationToken cancellationToken = default)
    {
        if (_transaction != null)
        {
            await _transaction.CommitAsync(cancellationToken);
            await _transaction.DisposeAsync();
            _transaction = null;
        }
    }

    public async Task RollbackTransactionAsync(CancellationToken cancellationToken = default)
    {
        if (_transaction != null)
        {
            await _transaction.RollbackAsync(cancellationToken);
            await _transaction.DisposeAsync();
            _transaction = null;
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed && disposing)
        {
            _transaction?.Dispose();
            _context.Dispose();
            _disposed = true;
        }
    }
}