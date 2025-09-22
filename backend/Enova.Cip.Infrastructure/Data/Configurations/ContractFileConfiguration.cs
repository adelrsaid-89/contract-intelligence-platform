using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class ContractFileConfiguration : IEntityTypeConfiguration<ContractFile>
{
    public void Configure(EntityTypeBuilder<ContractFile> builder)
    {
        builder.HasKey(cf => cf.Id);

        builder.Property(cf => cf.ObjectKey)
            .IsRequired()
            .HasMaxLength(500);

        builder.Property(cf => cf.OriginalFileName)
            .IsRequired()
            .HasMaxLength(255);

        builder.Property(cf => cf.ContentType)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(cf => cf.Hash)
            .IsRequired()
            .HasMaxLength(128);

        builder.Property(cf => cf.FolderType)
            .HasConversion<int>();

        builder.Property(cf => cf.UploadedAt)
            .IsRequired();

        builder.HasOne(cf => cf.Contract)
            .WithMany(c => c.Files)
            .HasForeignKey(cf => cf.ContractId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(cf => cf.UploadedByUser)
            .WithMany(u => u.UploadedFiles)
            .HasForeignKey(cf => cf.UploadedBy)
            .OnDelete(DeleteBehavior.Restrict);
    }
}