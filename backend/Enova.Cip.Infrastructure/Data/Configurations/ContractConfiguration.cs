using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class ContractConfiguration : IEntityTypeConfiguration<Contract>
{
    public void Configure(EntityTypeBuilder<Contract> builder)
    {
        builder.HasKey(c => c.Id);

        builder.Property(c => c.Title)
            .IsRequired()
            .HasMaxLength(300);

        builder.Property(c => c.ContractValue)
            .HasPrecision(18, 2);

        builder.Property(c => c.PaymentTerms)
            .HasMaxLength(500);

        builder.Property(c => c.Status)
            .HasConversion<int>();

        builder.Property(c => c.CreatedAt)
            .IsRequired();

        builder.Property(c => c.UpdatedAt)
            .IsRequired();

        builder.HasOne(c => c.Project)
            .WithMany(p => p.Contracts)
            .HasForeignKey(c => c.ProjectId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(c => c.Files)
            .WithOne(cf => cf.Contract)
            .HasForeignKey(cf => cf.ContractId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(c => c.MetadataFields)
            .WithOne(mf => mf.Contract)
            .HasForeignKey(mf => mf.ContractId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(c => c.Obligations)
            .WithOne(o => o.Contract)
            .HasForeignKey(o => o.ContractId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}