using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class AssignmentConfiguration : IEntityTypeConfiguration<Assignment>
{
    public void Configure(EntityTypeBuilder<Assignment> builder)
    {
        builder.HasKey(a => a.Id);

        builder.Property(a => a.Status)
            .HasConversion<int>();

        builder.Property(a => a.PercentComplete)
            .HasDefaultValue(0);

        builder.Property(a => a.CreatedAt)
            .IsRequired();

        builder.Property(a => a.UpdatedAt)
            .IsRequired();

        builder.HasOne(a => a.Obligation)
            .WithMany(o => o.Assignments)
            .HasForeignKey(a => a.ObligationId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(a => a.AssigneeUser)
            .WithMany(u => u.Assignments)
            .HasForeignKey(a => a.AssigneeUserId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(a => a.Evidence)
            .WithOne(e => e.Assignment)
            .HasForeignKey(e => e.AssignmentId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(a => new { a.ObligationId, a.AssigneeUserId });
    }
}