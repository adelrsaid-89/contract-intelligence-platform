using Microsoft.Extensions.Logging;
using Moq;
using FluentAssertions;
using AutoMapper;
using Enova.Cip.Application.Services;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Application.Interfaces;
using Enova.Cip.Application.Common.Mappings;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;
using Enova.Cip.Domain.Interfaces;
using Enova.Cip.Tests.Common;

namespace Enova.Cip.Tests.UnitTests.Services;

public class ProjectServiceTests : IDisposable
{
    private readonly Mock<IUnitOfWork> _unitOfWorkMock;
    private readonly IMapper _mapper;
    private readonly Mock<IAuditService> _auditServiceMock;
    private readonly Mock<ILogger<ProjectService>> _loggerMock;
    private readonly ProjectService _projectService;
    private readonly TestFixture _fixture;

    public ProjectServiceTests()
    {
        _unitOfWorkMock = new Mock<IUnitOfWork>();
        _auditServiceMock = new Mock<IAuditService>();
        _loggerMock = new Mock<ILogger<ProjectService>>();
        _fixture = new TestFixture();

        // Setup AutoMapper
        var mapperConfig = new MapperConfiguration(cfg => cfg.AddProfile<MappingProfile>());
        _mapper = mapperConfig.CreateMapper();

        _projectService = new ProjectService(_unitOfWorkMock.Object, _mapper, _auditServiceMock.Object, _loggerMock.Object);
    }

    [Fact]
    public async Task GetUserProjectsAsync_ForRegularUser_ShouldReturnOnlyAccessibleProjects()
    {
        // Arrange
        var user = _fixture.Create<User>();
        user.Role = UserRole.User;

        var projects = _fixture.CreateMany<Project>(3).ToList();
        var permissions = new List<UserProjectPermission>
        {
            new() { UserId = user.Id, ProjectId = projects[0].Id, AccessLevel = AccessLevel.Owner },
            new() { UserId = user.Id, ProjectId = projects[1].Id, AccessLevel = AccessLevel.Viewer }
        };

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(user.Id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        _unitOfWorkMock.Setup(uow => uow.UserProjectPermissions.FindAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<UserProjectPermission, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(permissions);

        _unitOfWorkMock.Setup(uow => uow.Projects.FindAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<Project, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(projects.Take(2)); // Only projects user has access to

        _unitOfWorkMock.Setup(uow => uow.Contracts.CountAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<Contract, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(0);

        // Act
        var result = await _projectService.GetUserProjectsAsync(user.Id);

        // Assert
        result.Should().HaveCount(2);
        result.Should().AllSatisfy(p => p.UserPermissions.Should().NotBeEmpty());
    }

    [Fact]
    public async Task GetUserProjectsAsync_ForAdmin_ShouldReturnAllProjects()
    {
        // Arrange
        var adminUser = _fixture.Create<User>();
        adminUser.Role = UserRole.Admin;

        var projects = _fixture.CreateMany<Project>(3).ToList();

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(adminUser.Id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(adminUser);

        _unitOfWorkMock.Setup(uow => uow.Projects.GetAllAsync(It.IsAny<CancellationToken>()))
            .ReturnsAsync(projects);

        _unitOfWorkMock.Setup(uow => uow.Contracts.CountAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<Contract, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(0);

        _unitOfWorkMock.Setup(uow => uow.UserProjectPermissions.FindAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<UserProjectPermission, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<UserProjectPermission>());

        // Act
        var result = await _projectService.GetUserProjectsAsync(adminUser.Id);

        // Assert
        result.Should().HaveCount(3);
    }

    [Fact]
    public async Task CreateProjectAsync_ShouldCreateProjectAndGrantOwnerPermission()
    {
        // Arrange
        var createProjectDto = _fixture.Create<CreateProjectDto>();
        var userId = _fixture.Create<int>();
        var project = _mapper.Map<Project>(createProjectDto);
        project.Id = _fixture.Create<int>();

        _unitOfWorkMock.Setup(uow => uow.Projects.AddAsync(It.IsAny<Project>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(project);

        _unitOfWorkMock.Setup(uow => uow.UserProjectPermissions.AddAsync(
            It.IsAny<UserProjectPermission>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new UserProjectPermission());

        // Act
        var result = await _projectService.CreateProjectAsync(createProjectDto, userId);

        // Assert
        result.Should().NotBeNull();
        result.Name.Should().Be(createProjectDto.Name);
        result.ClientName.Should().Be(createProjectDto.ClientName);
        result.Country.Should().Be(createProjectDto.Country);

        _unitOfWorkMock.Verify(uow => uow.Projects.AddAsync(It.IsAny<Project>(), It.IsAny<CancellationToken>()), Times.Once);
        _unitOfWorkMock.Verify(uow => uow.UserProjectPermissions.AddAsync(
            It.Is<UserProjectPermission>(p => p.UserId == userId && p.AccessLevel == AccessLevel.Owner),
            It.IsAny<CancellationToken>()), Times.Once);
        _unitOfWorkMock.Verify(uow => uow.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Exactly(2));
        _auditServiceMock.Verify(a => a.LogAsync(
            userId, "CREATE", "Project", It.IsAny<int>(), createProjectDto, null, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task HasAccessAsync_WithValidPermission_ShouldReturnTrue()
    {
        // Arrange
        var userId = _fixture.Create<int>();
        var projectId = _fixture.Create<int>();
        var user = _fixture.Create<User>();
        user.Role = UserRole.User;

        var permission = new UserProjectPermission
        {
            UserId = userId,
            ProjectId = projectId,
            AccessLevel = AccessLevel.Manager
        };

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        _unitOfWorkMock.Setup(uow => uow.UserProjectPermissions.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<UserProjectPermission, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(permission);

        // Act
        var result = await _projectService.HasAccessAsync(projectId, userId, AccessLevel.Viewer);

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public async Task HasAccessAsync_ForAdmin_ShouldAlwaysReturnTrue()
    {
        // Arrange
        var userId = _fixture.Create<int>();
        var projectId = _fixture.Create<int>();
        var adminUser = _fixture.Create<User>();
        adminUser.Role = UserRole.Admin;

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(adminUser);

        // Act
        var result = await _projectService.HasAccessAsync(projectId, userId, AccessLevel.Owner);

        // Assert
        result.Should().BeTrue();
        _unitOfWorkMock.Verify(uow => uow.UserProjectPermissions.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<UserProjectPermission, bool>>>(),
            It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task HasAccessAsync_WithInsufficientPermission_ShouldReturnFalse()
    {
        // Arrange
        var userId = _fixture.Create<int>();
        var projectId = _fixture.Create<int>();
        var user = _fixture.Create<User>();
        user.Role = UserRole.User;

        var permission = new UserProjectPermission
        {
            UserId = userId,
            ProjectId = projectId,
            AccessLevel = AccessLevel.Viewer
        };

        _unitOfWorkMock.Setup(uow => uow.Users.GetByIdAsync(userId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(user);

        _unitOfWorkMock.Setup(uow => uow.UserProjectPermissions.FindFirstAsync(
            It.IsAny<System.Linq.Expressions.Expression<Func<UserProjectPermission, bool>>>(),
            It.IsAny<CancellationToken>()))
            .ReturnsAsync(permission);

        // Act
        var result = await _projectService.HasAccessAsync(projectId, userId, AccessLevel.Manager);

        // Assert
        result.Should().BeFalse();
    }

    public void Dispose()
    {
        // Cleanup if needed
    }
}