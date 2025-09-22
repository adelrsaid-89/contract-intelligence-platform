using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Enova.Cip.Domain.Interfaces;
using Enova.Cip.Infrastructure.Data;
using Enova.Cip.Infrastructure.Repositories;
using Enova.Cip.Infrastructure.Services;

namespace Enova.Cip.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        // Database
        services.AddDbContext<CipDbContext>(options =>
            options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

        // Repositories
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
        services.AddScoped<IUnitOfWork, UnitOfWork>();

        // External Services
        AddStorageService(services, configuration);
        AddSearchService(services, configuration);
        AddEmailService(services, configuration);
        AddAiService(services, configuration);

        return services;
    }

    private static void AddStorageService(IServiceCollection services, IConfiguration configuration)
    {
        var storageType = configuration.GetValue<string>("Storage:Type") ?? "Local";

        if (storageType.Equals("MinIO", StringComparison.OrdinalIgnoreCase))
        {
            services.Configure<MinioStorageOptions>(configuration.GetSection("Storage:MinIO"));
            services.AddSingleton<IStorageService, MinioStorageService>();
        }
        else
        {
            services.Configure<LocalStorageOptions>(configuration.GetSection("Storage:Local"));
            services.AddSingleton<IStorageService, LocalFileStorageService>();
        }
    }

    private static void AddSearchService(IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<ElasticsearchOptions>(configuration.GetSection("Elasticsearch"));
        services.AddSingleton<ISearchService, ElasticsearchService>();
    }

    private static void AddEmailService(IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<SmtpOptions>(configuration.GetSection("Smtp"));
        services.AddTransient<IEmailService, SmtpEmailService>();
    }

    private static void AddAiService(IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<AiServiceOptions>(configuration.GetSection("AiService"));
        services.AddHttpClient<IAiService, HttpAiService>();
    }
}