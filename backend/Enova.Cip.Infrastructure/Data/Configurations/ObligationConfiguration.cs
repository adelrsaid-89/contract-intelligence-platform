using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class ObligationConfiguration : IEntityTypeConfiguration<Obligation>
{
    public void Configure(EntityTypeBuilder<Obligation> builder)
    {
        builder.HasKey(o => o.Id);

        builder.Property(o => o.Description)
            .IsRequired()
            .HasMaxLength(2000);

        builder.Property(o => o.Frequency)
            .HasMaxLength(100);

        builder.Property(o => o.PenaltyText)
            .HasMaxLength(1000);

        builder.Property(o => o.Source)
            .HasConversion<int>();

        builder.Property(o => o.CreatedAt)
            .IsRequired();

        builder.Property(o => o.UpdatedAt)
            .IsRequired();

        builder.HasOne(o => o.Contract)
            .WithMany(c => c.Obligations)
            .HasForeignKey(o => o.ContractId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(o => o.Assignments)
            .WithOne(a => a.Obligation)
            .HasForeignKey(a => a.ObligationId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(o => o.PenaltyRisks)
            .WithOne(pr => pr.Obligation)
            .HasForeignKey(pr => pr.ObligationId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}