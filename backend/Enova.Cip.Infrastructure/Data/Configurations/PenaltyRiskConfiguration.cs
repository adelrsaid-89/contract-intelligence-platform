using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class PenaltyRiskConfiguration : IEntityTypeConfiguration<PenaltyRisk>
{
    public void Configure(EntityTypeBuilder<PenaltyRisk> builder)
    {
        builder.HasKey(pr => pr.Id);

        builder.Property(pr => pr.Basis)
            .IsRequired()
            .HasMaxLength(500);

        builder.Property(pr => pr.Amount)
            .HasPrecision(18, 2);

        builder.Property(pr => pr.ComputedAt)
            .IsRequired();

        builder.HasOne(pr => pr.Obligation)
            .WithMany(o => o.PenaltyRisks)
            .HasForeignKey(pr => pr.ObligationId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(pr => new { pr.ObligationId, pr.ComputedAt });
    }
}