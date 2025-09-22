using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Serilog;
using System.Text;
using Hangfire;
using Hangfire.PostgreSql;
using Enova.Cip.Application;
using Enova.Cip.Infrastructure;
using Enova.Cip.Infrastructure.Data;
using Enova.Cip.Api.Middleware;
using Enova.Cip.Api.Jobs;
using Enova.Cip.Domain.Enums;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/cip-.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
builder.Services.AddControllers();

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Contract Intelligence Platform API",
        Version = "v1",
        Description = "API for managing contracts, obligations, and assignments"
    });

    // Add JWT authentication
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\"",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                },
                Scheme = "oauth2",
                Name = "Bearer",
                In = ParameterLocation.Header,
            },
            new List<string>()
        }
    });
});

// Add Application and Infrastructure services
builder.Services.AddApplication();
builder.Services.AddInfrastructure(builder.Configuration);

// Add Authentication
var jwtSecret = builder.Configuration["Jwt:Secret"] ?? throw new InvalidOperationException("JWT Secret not configured");
var key = Encoding.ASCII.GetBytes(jwtSecret);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.RequireHttpsMetadata = false;
    options.SaveToken = true;
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(key),
        ValidateIssuer = false,
        ValidateAudience = false,
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

// Add CORS
var corsOrigins = builder.Configuration.GetSection("Cors:Origins").Get<string[]>() ?? new[] { "*" };
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(corsOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

// Add Hangfire
builder.Services.AddHangfire(configuration => configuration
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UsePostgreSqlStorage(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddHangfireServer();

// Add background job service
builder.Services.AddScoped<IBackgroundJobService, BackgroundJobService>();

// Add API versioning
builder.Services.AddApiVersioning(opt =>
{
    opt.DefaultApiVersion = new Microsoft.AspNetCore.Mvc.ApiVersion(1, 0);
    opt.AssumeDefaultVersionWhenUnspecified = true;
    opt.ApiVersionReader = Microsoft.AspNetCore.Mvc.ApiVersionReader.Combine(
        new Microsoft.AspNetCore.Mvc.QueryStringApiVersionReader("apiVersion"),
        new Microsoft.AspNetCore.Mvc.HeaderApiVersionReader("X-Version"),
        new Microsoft.AspNetCore.Mvc.UrlSegmentApiVersionReader());
});

builder.Services.AddVersionedApiExplorer(setup =>
{
    setup.GroupNameFormat = "'v'VVV";
    setup.SubstituteApiVersionInUrl = true;
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "CIP API V1");
        c.RoutePrefix = string.Empty; // Set Swagger UI at the app root
    });
}

// Middleware pipeline
app.UseMiddleware<ExceptionHandlingMiddleware>();
app.UseMiddleware<RequestLoggingMiddleware>();

app.UseHttpsRedirection();
app.UseCors();

app.UseAuthentication();
app.UseAuthorization();

app.UseMiddleware<AuditMiddleware>();

// Hangfire Dashboard (Admin only)
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() }
});

app.MapControllers();

// Serve static files for local file storage
app.UseStaticFiles();

// Initialize database and seed data
await InitializeDatabaseAsync(app);

// Schedule recurring jobs
await ScheduleRecurringJobsAsync(app);

app.Run();

// Database initialization
async Task InitializeDatabaseAsync(WebApplication app)
{
    using var scope = app.Services.CreateScope();
    var context = scope.ServiceProvider.GetRequiredService<CipDbContext>();

    try
    {
        await context.Database.MigrateAsync();

        // Seed data if SEED_MODE environment variable is set
        var seedMode = Environment.GetEnvironmentVariable("SEED_MODE");
        if (!string.IsNullOrEmpty(seedMode))
        {
            await SeedDataAsync(context);
        }

        Log.Information("Database initialized successfully");
    }
    catch (Exception ex)
    {
        Log.Fatal(ex, "An error occurred while initializing the database");
        throw;
    }
}

// Seed initial data
async Task SeedDataAsync(CipDbContext context)
{
    // Check if data already exists
    if (await context.Users.AnyAsync())
    {
        return;
    }

    // Create admin user
    var adminUser = new Enova.Cip.Domain.Entities.User
    {
        Name = "System Administrator",
        Email = "admin@enova.com",
        Role = UserRole.Admin,
        PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
        IsActive = true,
        CreatedAt = DateTime.UtcNow
    };

    context.Users.Add(adminUser);
    await context.SaveChangesAsync();

    Log.Information("Seed data created successfully");
}

// Schedule recurring background jobs
async Task ScheduleRecurringJobsAsync(WebApplication app)
{
    using var scope = app.Services.CreateScope();
    var backgroundJobService = scope.ServiceProvider.GetRequiredService<IBackgroundJobService>();

    await backgroundJobService.ScheduleReminderJobs();
    await backgroundJobService.SchedulePenaltyRiskJobs();
    await backgroundJobService.ScheduleSearchIndexerJobs();
    await backgroundJobService.ScheduleNotificationCleanupJobs();

    Log.Information("Recurring jobs scheduled successfully");
}

// Hangfire authorization filter
public class HangfireAuthorizationFilter : IDashboardAuthorizationFilter
{
    public bool Authorize(DashboardContext context)
    {
        var httpContext = context.GetHttpContext();

        // In development, allow access without authentication
        if (httpContext.RequestServices.GetRequiredService<IWebHostEnvironment>().IsDevelopment())
        {
            return true;
        }

        // In production, require admin role
        return httpContext.User.Identity?.IsAuthenticated == true &&
               httpContext.User.IsInRole(UserRole.Admin.ToString());
    }
}