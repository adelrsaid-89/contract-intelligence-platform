namespace Enova.Cip.Domain.Enums;

public enum UserRole
{
    Admin = 0,
    Manager = 1,
    User = 2
}

public enum ProjectStatus
{
    Active = 0,
    Closed = 1
}

public enum AccessLevel
{
    Owner = 0,
    Manager = 1,
    Viewer = 2
}

public enum ContractStatus
{
    Draft = 0,
    Active = 1,
    Expired = 2,
    Terminated = 3
}

public enum FolderType
{
    Contract = 0,
    AMC = 1
}

public enum DataSource
{
    AI = 0,
    Human = 1
}

public enum AssignmentStatus
{
    Open = 0,
    InProgress = 1,
    Done = 2,
    Overdue = 3,
    Closed = 4
}

public enum NotificationType
{
    AssignmentCreated = 0,
    AssignmentReminder = 1,
    AssignmentOverdue = 2,
    ContractExpiring = 3,
    PenaltyRisk = 4,
    General = 5
}

public enum NotificationStatus
{
    Pending = 0,
    Sent = 1,
    Failed = 2
}