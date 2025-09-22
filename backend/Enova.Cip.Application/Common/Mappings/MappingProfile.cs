using AutoMapper;
using Enova.Cip.Application.DTOs;
using Enova.Cip.Domain.Entities;

namespace Enova.Cip.Application.Common.Mappings;

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        CreateMap<User, UserDto>();
        CreateMap<CreateUserDto, User>();
        CreateMap<UpdateUserDto, User>();

        CreateMap<Project, ProjectDto>();
        CreateMap<CreateProjectDto, Project>();
        CreateMap<UpdateProjectDto, Project>();

        CreateMap<Contract, ContractDto>();
        CreateMap<CreateContractDto, Contract>();
        CreateMap<UpdateContractDto, Contract>();

        CreateMap<ContractFile, ContractFileDto>();

        CreateMap<Obligation, ObligationDto>();
        CreateMap<CreateObligationDto, Obligation>();
        CreateMap<UpdateObligationDto, Obligation>();

        CreateMap<Assignment, AssignmentDto>();
        CreateMap<CreateAssignmentDto, Assignment>();
        CreateMap<UpdateAssignmentDto, Assignment>();

        CreateMap<Evidence, EvidenceDto>();

        CreateMap<MetadataField, MetadataFieldDto>();

        CreateMap<Notification, NotificationDto>();

        CreateMap<PenaltyRisk, PenaltyRiskDto>();

        CreateMap<AuditLog, AuditLogDto>();

        CreateMap<UserProjectPermission, UserProjectPermissionDto>();
    }
}