using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using System.Net.Http.Json;
using System.Net;
using System.Text;
using System.Text.Json;
using FluentAssertions;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Infrastructure.Data;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;
using Enova.Cip.Tests.Common;

namespace Enova.Cip.Tests.IntegrationTests.Api;

public class AuthControllerTests : IClassFixture<WebApplicationFactory<Program>>, IDisposable
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;
    private readonly CipDbContext _context;

    public AuthControllerTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = _factory.CreateClient();

        // Get the test database context
        var scope = _factory.Services.CreateScope();
        _context = scope.ServiceProvider.GetRequiredService<CipDbContext>();

        SeedTestData();
    }

    private void SeedTestData()
    {
        // Clear existing data
        _context.Users.RemoveRange(_context.Users);
        _context.SaveChanges();

        // Add test user
        var testUser = new User
        {
            Name = "Test User",
            Email = "test@example.com",
            Role = UserRole.User,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("Test123!"),
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };

        _context.Users.Add(testUser);
        _context.SaveChanges();
    }

    [Fact]
    public async Task Login_WithValidCredentials_ShouldReturnToken()
    {
        // Arrange
        var loginDto = new LoginDto
        {
            Email = "test@example.com",
            Password = "Test123!"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginDto);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var authResponse = await response.Content.ReadFromJsonAsync<AuthResponseDto>();
        authResponse.Should().NotBeNull();
        authResponse!.Token.Should().NotBeNullOrEmpty();
        authResponse.RefreshToken.Should().NotBeNullOrEmpty();
        authResponse.User.Should().NotBeNull();
        authResponse.User.Email.Should().Be("test@example.com");
        authResponse.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
    }

    [Fact]
    public async Task Login_WithInvalidCredentials_ShouldReturnUnauthorized()
    {
        // Arrange
        var loginDto = new LoginDto
        {
            Email = "test@example.com",
            Password = "WrongPassword"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginDto);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task Login_WithInvalidEmail_ShouldReturnBadRequest()
    {
        // Arrange
        var loginDto = new LoginDto
        {
            Email = "invalid-email",
            Password = "Test123!"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/login", loginDto);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetMe_WithValidToken_ShouldReturnUserInfo()
    {
        // Arrange
        var token = await GetValidTokenAsync();
        _client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.GetAsync("/api/auth/me");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        user.Should().NotBeNull();
        user!.Email.Should().Be("test@example.com");
    }

    [Fact]
    public async Task GetMe_WithoutToken_ShouldReturnUnauthorized()
    {
        // Act
        var response = await _client.GetAsync("/api/auth/me");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task RefreshToken_WithValidRefreshToken_ShouldReturnNewToken()
    {
        // Arrange
        var authResponse = await LoginAndGetAuthResponseAsync();
        var refreshRequest = new { RefreshToken = authResponse.RefreshToken };

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/refresh", refreshRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var newAuthResponse = await response.Content.ReadFromJsonAsync<AuthResponseDto>();
        newAuthResponse.Should().NotBeNull();
        newAuthResponse!.Token.Should().NotBeNullOrEmpty();
        newAuthResponse.Token.Should().NotBe(authResponse.Token);
        newAuthResponse.RefreshToken.Should().NotBeNullOrEmpty();
        newAuthResponse.RefreshToken.Should().NotBe(authResponse.RefreshToken);
    }

    [Fact]
    public async Task Logout_WithValidRefreshToken_ShouldSucceed()
    {
        // Arrange
        var authResponse = await LoginAndGetAuthResponseAsync();
        var token = authResponse.Token;
        var refreshRequest = new { RefreshToken = authResponse.RefreshToken };

        _client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.PostAsJsonAsync("/api/auth/logout", refreshRequest);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verify refresh token is invalidated
        var refreshResponse = await _client.PostAsJsonAsync("/api/auth/refresh", refreshRequest);
        refreshResponse.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    private async Task<string> GetValidTokenAsync()
    {
        var authResponse = await LoginAndGetAuthResponseAsync();
        return authResponse.Token;
    }

    private async Task<AuthResponseDto> LoginAndGetAuthResponseAsync()
    {
        var loginDto = new LoginDto
        {
            Email = "test@example.com",
            Password = "Test123!"
        };

        var response = await _client.PostAsJsonAsync("/api/auth/login", loginDto);
        response.EnsureSuccessStatusCode();

        var authResponse = await response.Content.ReadFromJsonAsync<AuthResponseDto>();
        return authResponse!;
    }

    public void Dispose()
    {
        _context.Dispose();
        _client.Dispose();
    }
}