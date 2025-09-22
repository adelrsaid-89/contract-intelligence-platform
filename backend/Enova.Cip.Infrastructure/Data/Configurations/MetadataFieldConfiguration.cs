using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class MetadataFieldConfiguration : IEntityTypeConfiguration<MetadataField>
{
    public void Configure(EntityTypeBuilder<MetadataField> builder)
    {
        builder.HasKey(mf => mf.Id);

        builder.Property(mf => mf.Key)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(mf => mf.Value)
            .IsRequired()
            .HasMaxLength(1000);

        builder.Property(mf => mf.Source)
            .HasConversion<int>();

        builder.Property(mf => mf.OffsetsJson)
            .HasColumnType("jsonb");

        builder.Property(mf => mf.CreatedAt)
            .IsRequired();

        builder.Property(mf => mf.UpdatedAt)
            .IsRequired();

        builder.HasOne(mf => mf.Contract)
            .WithMany(c => c.MetadataFields)
            .HasForeignKey(mf => mf.ContractId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(mf => new { mf.ContractId, mf.Key });
    }
}