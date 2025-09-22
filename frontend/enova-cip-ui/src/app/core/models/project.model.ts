export interface Project {
  id: string;
  name: string;
  description?: string;
  code: string;
  status: ProjectStatus;
  startDate: Date;
  endDate?: Date;
  managerId: string;
  managerName: string;
  contractorIds: string[];
  totalContracts: number;
  totalObligations: number;
  complianceRate: number;
  riskLevel: RiskLevel;
  budget?: number;
  location?: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum ProjectStatus {
  PLANNING = 'planning',
  ACTIVE = 'active',
  ON_HOLD = 'on_hold',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface ProjectPermission {
  userId: string;
  projectId: string;
  permissions: string[];
  assignedAt: Date;
  assignedBy: string;
}

export interface ProjectStats {
  projectId: string;
  totalContracts: number;
  activeContracts: number;
  totalObligations: number;
  completedObligations: number;
  overdueObligations: number;
  upcomingObligations: number;
  complianceRate: number;
  penaltyRisk: number;
  lastUpdated: Date;
}

export interface ProjectDashboard {
  project: Project;
  stats: ProjectStats;
  recentActivity: ActivityLog[];
  upcomingDeadlines: Obligation[];
  riskAlerts: RiskAlert[];
}

export interface ActivityLog {
  id: string;
  projectId: string;
  userId: string;
  userName: string;
  action: string;
  entityType: string;
  entityId: string;
  description: string;
  timestamp: Date;
  metadata?: any;
}

export interface RiskAlert {
  id: string;
  projectId: string;
  type: 'overdue' | 'upcoming' | 'penalty' | 'compliance';
  severity: RiskLevel;
  title: string;
  description: string;
  relatedEntityType: string;
  relatedEntityId: string;
  dueDate?: Date;
  createdAt: Date;
}