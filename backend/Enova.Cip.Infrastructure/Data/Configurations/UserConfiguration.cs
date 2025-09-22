using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.HasKey(u => u.Id);

        builder.Property(u => u.Name)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(u => u.Email)
            .IsRequired()
            .HasMaxLength(255);

        builder.Property(u => u.PasswordHash)
            .IsRequired()
            .HasMaxLength(255);

        builder.Property(u => u.Role)
            .HasConversion<int>();

        builder.Property(u => u.CreatedAt)
            .IsRequired();

        builder.HasIndex(u => u.Email)
            .IsUnique();

        builder.HasMany(u => u.ProjectPermissions)
            .WithOne(p => p.User)
            .HasForeignKey(p => p.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(u => u.Assignments)
            .WithOne(a => a.AssigneeUser)
            .HasForeignKey(a => a.AssigneeUserId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(u => u.UploadedFiles)
            .WithOne(cf => cf.UploadedByUser)
            .HasForeignKey(cf => cf.UploadedBy)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(u => u.UploadedEvidence)
            .WithOne(e => e.UploadedByUser)
            .HasForeignKey(e => e.UploadedBy)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(u => u.Notifications)
            .WithOne(n => n.User)
            .HasForeignKey(n => n.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(u => u.AuditLogs)
            .WithOne(al => al.Actor)
            .HasForeignKey(al => al.ActorId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}