using AutoFixture;
using AutoFixture.Xunit2;
using Enova.Cip.Domain.Entities;
using Enova.Cip.Domain.Enums;

namespace Enova.Cip.Tests.Common;

public class TestFixture : IFixture
{
    private readonly Fixture _fixture;

    public TestFixture()
    {
        _fixture = new Fixture();
        CustomizeFixture();
    }

    private void CustomizeFixture()
    {
        // Customize User
        _fixture.Customize<User>(composer => composer
            .With(u => u.Email, _fixture.Create<string>() + "@test.com")
            .With(u => u.Role, UserRole.User)
            .With(u => u.IsActive, true)
            .Without(u => u.ProjectPermissions)
            .Without(u => u.Assignments)
            .Without(u => u.UploadedFiles)
            .Without(u => u.UploadedEvidence)
            .Without(u => u.Notifications)
            .Without(u => u.AuditLogs));

        // Customize Project
        _fixture.Customize<Project>(composer => composer
            .With(p => p.Status, ProjectStatus.Active)
            .Without(p => p.UserPermissions)
            .Without(p => p.Contracts));

        // Customize Contract
        _fixture.Customize<Contract>(composer => composer
            .With(c => c.Status, ContractStatus.Active)
            .Without(c => c.Project)
            .Without(c => c.Files)
            .Without(c => c.MetadataFields)
            .Without(c => c.Obligations));

        // Customize Obligation
        _fixture.Customize<Obligation>(composer => composer
            .With(o => o.Source, DataSource.Human)
            .Without(o => o.Contract)
            .Without(o => o.Assignments)
            .Without(o => o.PenaltyRisks));

        // Customize Assignment
        _fixture.Customize<Assignment>(composer => composer
            .With(a => a.Status, AssignmentStatus.Open)
            .With(a => a.PercentComplete, 0)
            .Without(a => a.Obligation)
            .Without(a => a.AssigneeUser)
            .Without(a => a.Evidence));
    }

    public T Create<T>() => _fixture.Create<T>();
    public IEnumerable<T> CreateMany<T>(int count) => _fixture.CreateMany<T>(count);
    public T Build<T>() => _fixture.Build<T>().Create();

    // Delegate all other IFixture members to the internal fixture
    public ICustomizationComposer<T> Build<T>() => _fixture.Build<T>();
    public object Create(object request, ISpecimenContext context) => _fixture.Create(request, context);
    public T Create<T>(ISpecimenBuilder builder) => _fixture.Create<T>(builder);
    public object Create(Type t) => _fixture.Create(t);
    public void Inject<T>(T item) => _fixture.Inject(item);
    public void Customize<T>(Func<ICustomizationComposer<T>, ISpecimenBuilder> composer) => _fixture.Customize(composer);
    public void Customize(ICustomization customization) => _fixture.Customize(customization);
    public IFixture Freeze<T>() => _fixture.Freeze<T>();
    public T Freeze<T>() => _fixture.Freeze<T>();
    public IEnumerable<T> CreateMany<T>() => _fixture.CreateMany<T>();
    public void RepeatCount { get => _fixture.RepeatCount; set => _fixture.RepeatCount = value; }
    public IList<ISpecimenBuilder> Customizations => _fixture.Customizations;
    public IList<ISpecimenBuilder> ResidueCollectors => _fixture.ResidueCollectors;
    public IList<ISpecimenBuilderTransformation> Behaviors => _fixture.Behaviors;
    public bool OmitAutoProperties { get => _fixture.OmitAutoProperties; set => _fixture.OmitAutoProperties = value; }
}

public class AutoDataAttribute : AutoFixture.Xunit2.AutoDataAttribute
{
    public AutoDataAttribute() : base(() => new TestFixture())
    {
    }
}