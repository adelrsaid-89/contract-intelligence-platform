using Microsoft.EntityFrameworkCore;
using Enova.Cip.Infrastructure.Data;

namespace Enova.Cip.Tests.Common;

public static class TestDbContextFactory
{
    public static CipDbContext Create()
    {
        var options = new DbContextOptionsBuilder<CipDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;

        var context = new CipDbContext(options);
        context.Database.EnsureCreated();

        return context;
    }

    public static void Destroy(CipDbContext context)
    {
        context.Database.EnsureDeleted();
        context.Dispose();
    }
}