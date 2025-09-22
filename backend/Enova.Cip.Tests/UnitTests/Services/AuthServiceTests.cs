using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using FluentAssertions;
using AutoMapper;
using Enova.Cip.Application.Services;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Common.Mappings;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;
using Enova.Cip.Domain.Interfaces;
using Enova.Cip.Tests.Common;

namespace Enova.Cip.Tests.UnitTests.Services;

public class AuthServiceTests : IDisposable
{
    private readonly Mock<IUnitOfWork> _unitOfWorkMock;
    private readonly IMapper _mapper;
    private readonly Mock<IConfiguration> _configurationMock;
    private readonly Mock<ILogger<AuthService>> _loggerMock;
    private readonly AuthService _authService;
    private readonly TestFixture _fixture;

    public AuthServiceTests()
    {
        _unitOfWorkMock = new Mock<IUnitOfWork>();
        _configurationMock = new Mock<IConfiguration>();
        _loggerMock = new Mock<ILogger<AuthService>>();
        _fixture = new TestFixture();

        // Setup AutoMapper
        var mapperConfig = new MapperConfiguration(cfg => cfg.AddProfile<MappingProfile>());
        _mapper = mapperConfig.CreateMapper();

        // Setup Configuration
        _configurationMock.Setup(c => c["Jwt:Secret"]).Returns("TestSecretKeyThatIsAtLeast32CharactersLong123!");
        _configurationMock.Setup(c => c["Jwt:ExpiryMinutes"]).Returns("60");

        _authService = new AuthService(_unitOfWorkMock.Object, _mapper, _configurationMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task LoginAsync_WithValidCredentials_ShouldReturnAuthResponse()
    {
        // Arrange
        var user = _fixture.Create<User>();
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword("password123");
        user.IsActive = true;

        var loginDto = new LoginDto
        {
            Email = user.Email,
            Password = "password123"
        };

        _unitOfWorkMock.Setup(uow => uow.Users.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<User, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        // Act
        var result = await _authService.LoginAsync(loginDto);

        // Assert
        result.Should().NotBeNull();
        result.Token.Should().NotBeNullOrEmpty();
        result.RefreshToken.Should().NotBeNullOrEmpty();
        result.User.Should().NotBeNull();
        result.User.Email.Should().Be(user.Email);
        result.ExpiresAt.Should().BeAfter(DateTime.UtcNow);
    }

    [Fact]
    public async Task LoginAsync_WithInvalidPassword_ShouldThrowUnauthorizedAccessException()
    {
        // Arrange
        var user = _fixture.Create<User>();
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword("correctpassword");
        user.IsActive = true;

        var loginDto = new LoginDto
        {
            Email = user.Email,
            Password = "wrongpassword"
        };

        _unitOfWorkMock.Setup(uow => uow.Users.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<User, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        // Act & Assert
        await _authService.Invoking(s => s.LoginAsync(loginDto))
            .Should().ThrowAsync<UnauthorizedAccessException>()
            .WithMessage("Invalid email or password");
    }

    [Fact]
    public async Task LoginAsync_WithInactiveUser_ShouldThrowUnauthorizedAccessException()
    {
        // Arrange
        var user = _fixture.Create<User>();
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword("password123");
        user.IsActive = false;

        var loginDto = new LoginDto
        {
            Email = user.Email,
            Password = "password123"
        };

        _unitOfWorkMock.Setup(uow => uow.Users.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<User, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync((User?)null); // User not found due to IsActive filter

        // Act & Assert
        await _authService.Invoking(s => s.LoginAsync(loginDto))
            .Should().ThrowAsync<UnauthorizedAccessException>()
            .WithMessage("Invalid email or password");
    }

    [Fact]
    public async Task GetCurrentUserAsync_WithValidUserId_ShouldReturnUserDto()
    {
        // Arrange
        var user = _fixture.Create<User>();

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(user.Id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        // Act
        var result = await _authService.GetCurrentUserAsync(user.Id);

        // Assert
        result.Should().NotBeNull();
        result.Id.Should().Be(user.Id);
        result.Email.Should().Be(user.Email);
        result.Name.Should().Be(user.Name);
        result.Role.Should().Be(user.Role);
    }

    [Fact]
    public async Task GetCurrentUserAsync_WithInvalidUserId_ShouldThrowUnauthorizedAccessException()
    {
        // Arrange
        var userId = 999;

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync((User?)null);

        // Act & Assert
        await _authService.Invoking(s => s.GetCurrentUserAsync(userId))
            .Should().ThrowAsync<UnauthorizedAccessException>()
            .WithMessage("User not found");
    }

    public void Dispose()
    {
        // Cleanup if needed
    }
}