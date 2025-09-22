using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Infrastructure.Data.Configurations;

public class EvidenceConfiguration : IEntityTypeConfiguration<Evidence>
{
    public void Configure(EntityTypeBuilder<Evidence> builder)
    {
        builder.HasKey(e => e.Id);

        builder.Property(e => e.ObjectKey)
            .IsRequired()
            .HasMaxLength(500);

        builder.Property(e => e.OriginalFileName)
            .IsRequired()
            .HasMaxLength(255);

        builder.Property(e => e.ContentType)
            .IsRequired()
            .HasMaxLength(100);

        builder.Property(e => e.Note)
            .HasMaxLength(1000);

        builder.Property(e => e.UploadedAt)
            .IsRequired();

        builder.HasOne(e => e.Assignment)
            .WithMany(a => a.Evidence)
            .HasForeignKey(e => e.AssignmentId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(e => e.UploadedByUser)
            .WithMany(u => u.UploadedEvidence)
            .HasForeignKey(e => e.UploadedBy)
            .OnDelete(DeleteBehavior.Restrict);
    }
}