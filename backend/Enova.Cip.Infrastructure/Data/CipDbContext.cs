using Microsoft.EntityFrameworkCore;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Infrastructure.Data.Configurations;

namespace Enova.Cip.Infrastructure.Data;

public class CipDbContext : DbContext
{
    public CipDbContext(DbContextOptions<CipDbContext> options) : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Project> Projects { get; set; }
    public DbSet<UserProjectPermission> UserProjectPermissions { get; set; }
    public DbSet<Contract> Contracts { get; set; }
    public DbSet<ContractFile> ContractFiles { get; set; }
    public DbSet<MetadataField> MetadataFields { get; set; }
    public DbSet<Obligation> Obligations { get; set; }
    public DbSet<Assignment> Assignments { get; set; }
    public DbSet<Evidence> Evidence { get; set; }
    public DbSet<Notification> Notifications { get; set; }
    public DbSet<PenaltyRisk> PenaltyRisks { get; set; }
    public DbSet<AuditLog> AuditLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.ApplyConfiguration(new UserConfiguration());
        modelBuilder.ApplyConfiguration(new ProjectConfiguration());
        modelBuilder.ApplyConfiguration(new UserProjectPermissionConfiguration());
        modelBuilder.ApplyConfiguration(new ContractConfiguration());
        modelBuilder.ApplyConfiguration(new ContractFileConfiguration());
        modelBuilder.ApplyConfiguration(new MetadataFieldConfiguration());
        modelBuilder.ApplyConfiguration(new ObligationConfiguration());
        modelBuilder.ApplyConfiguration(new AssignmentConfiguration());
        modelBuilder.ApplyConfiguration(new EvidenceConfiguration());
        modelBuilder.ApplyConfiguration(new NotificationConfiguration());
        modelBuilder.ApplyConfiguration(new PenaltyRiskConfiguration());
        modelBuilder.ApplyConfiguration(new AuditLogConfiguration());
    }
}