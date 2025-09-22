using FluentValidation;
using Enova.Cip.Application.DTOs;

namespace Enova.Cip.Application.Validators;

public class CreateUserDtoValidator : AbstractValidator<CreateUserDto>
{
    public CreateUserDtoValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required")
            .MaximumLength(100).WithMessage("Name must not exceed 100 characters");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Email format is invalid")
            .MaximumLength(255).WithMessage("Email must not exceed 255 characters");

        RuleFor(x => x.Password)
            .NotEmpty().WithMessage("Password is required")
            .MinimumLength(8).WithMessage("Password must be at least 8 characters")
            .Matches(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]")
            .WithMessage("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character");

        RuleFor(x => x.Role)
            .IsInEnum().WithMessage("Invalid role");
    }
}

public class LoginDtoValidator : AbstractValidator<LoginDto>
{
    public LoginDtoValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Email format is invalid");

        RuleFor(x => x.Password)
            .NotEmpty().WithMessage("Password is required");
    }
}

public class CreateProjectDtoValidator : AbstractValidator<CreateProjectDto>
{
    public CreateProjectDtoValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Project name is required")
            .MaximumLength(200).WithMessage("Project name must not exceed 200 characters");

        RuleFor(x => x.ClientName)
            .NotEmpty().WithMessage("Client name is required")
            .MaximumLength(200).WithMessage("Client name must not exceed 200 characters");

        RuleFor(x => x.Country)
            .NotEmpty().WithMessage("Country is required")
            .MaximumLength(100).WithMessage("Country must not exceed 100 characters");
    }
}

public class CreateContractDtoValidator : AbstractValidator<CreateContractDto>
{
    public CreateContractDtoValidator()
    {
        RuleFor(x => x.ProjectId)
            .GreaterThan(0).WithMessage("Valid project ID is required");

        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Contract title is required")
            .MaximumLength(300).WithMessage("Contract title must not exceed 300 characters");

        RuleFor(x => x.ContractValue)
            .GreaterThan(0).When(x => x.ContractValue.HasValue)
            .WithMessage("Contract value must be greater than 0");

        RuleFor(x => x.StartDate)
            .LessThan(x => x.EndDate).When(x => x.StartDate.HasValue && x.EndDate.HasValue)
            .WithMessage("Start date must be before end date");

        RuleFor(x => x.PaymentTerms)
            .MaximumLength(500).WithMessage("Payment terms must not exceed 500 characters");
    }
}

public class CreateObligationDtoValidator : AbstractValidator<CreateObligationDto>
{
    public CreateObligationDtoValidator()
    {
        RuleFor(x => x.ContractId)
            .GreaterThan(0).WithMessage("Valid contract ID is required");

        RuleFor(x => x.Description)
            .NotEmpty().WithMessage("Obligation description is required")
            .MaximumLength(2000).WithMessage("Description must not exceed 2000 characters");

        RuleFor(x => x.Frequency)
            .MaximumLength(100).WithMessage("Frequency must not exceed 100 characters");

        RuleFor(x => x.PenaltyText)
            .MaximumLength(1000).WithMessage("Penalty text must not exceed 1000 characters");
    }
}

public class CreateAssignmentDtoValidator : AbstractValidator<CreateAssignmentDto>
{
    public CreateAssignmentDtoValidator()
    {
        RuleFor(x => x.ObligationId)
            .GreaterThan(0).WithMessage("Valid obligation ID is required");

        RuleFor(x => x.AssigneeUserId)
            .GreaterThan(0).WithMessage("Valid assignee user ID is required");
    }
}