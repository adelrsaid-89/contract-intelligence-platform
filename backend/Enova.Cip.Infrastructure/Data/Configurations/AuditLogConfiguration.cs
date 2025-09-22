using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class AuditLogConfiguration : IEntityTypeConfiguration<AuditLog>
{
    public void Configure(EntityTypeBuilder<AuditLog> builder)
    {
        builder.HasKey(al => al.Id);

        builder.Property(al => al.Action)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(al => al.EntityType)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(al => al.PayloadJson)
            .HasColumnType("jsonb");

        builder.Property(al => al.IpAddress)
            .HasMaxLength(45);

        builder.Property(al => al.CreatedAt)
            .IsRequired();

        builder.HasOne(al => al.Actor)
            .WithMany(u => u.AuditLogs)
            .HasForeignKey(al => al.ActorId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(al => al.CreatedAt);
        builder.HasIndex(al => new { al.EntityType, al.EntityId });
        builder.HasIndex(al => al.ActorId);
    }
}