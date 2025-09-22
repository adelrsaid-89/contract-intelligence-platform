using Microsoft.Extensions.DependencyInjection;
using FluentValidation;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Application.Services;
using Enova.Cip.Application.Common.Mappings;

namespace Enova.Cip.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        // AutoMapper
        services.AddAutoMapper(typeof(MappingProfile));

        // FluentValidation
        services.AddValidatorsFromAssemblyContaining<MappingProfile>();

        // Application Services
        services.AddScoped<IAuthService, AuthService>();
        services.AddScoped<IProjectService, ProjectService>();
        services.AddScoped<IAuditService, AuditService>();
        services.AddScoped<IDashboardService, DashboardService>();

        return services;
    }
}