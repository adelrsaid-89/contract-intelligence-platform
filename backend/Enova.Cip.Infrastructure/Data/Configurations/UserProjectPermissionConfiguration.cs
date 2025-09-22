using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class UserProjectPermissionConfiguration : IEntityTypeConfiguration<UserProjectPermission>
{
    public void Configure(EntityTypeBuilder<UserProjectPermission> builder)
    {
        builder.HasKey(up => up.Id);

        builder.Property(up => up.AccessLevel)
            .HasConversion<int>();

        builder.Property(up => up.GrantedAt)
            .IsRequired();

        builder.HasIndex(up => new { up.UserId, up.ProjectId })
            .IsUnique();

        builder.HasOne(up => up.User)
            .WithMany(u => u.ProjectPermissions)
            .HasForeignKey(up => up.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(up => up.Project)
            .WithMany(p => p.UserPermissions)
            .HasForeignKey(up => up.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}