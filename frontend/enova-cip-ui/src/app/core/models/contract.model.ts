export interface Contract {
  id: string;
  projectId: string;
  projectName: string;
  title: string;
  contractNumber: string;
  description?: string;
  contractorId: string;
  contractorName: string;
  type: ContractType;
  status: ContractStatus;
  startDate: Date;
  endDate: Date;
  value: number;
  currency: string;
  files: ContractFile[];
  metadata: ContractMetadata;
  obligations: Obligation[];
  version: number;
  parentContractId?: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy: string;
}

export enum ContractType {
  MAIN_CONTRACT = 'main_contract',
  AMENDMENT = 'amendment',
  ADDENDUM = 'addendum',
  EXTENSION = 'extension'
}

export enum ContractStatus {
  DRAFT = 'draft',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  TERMINATED = 'terminated',
  EXPIRED = 'expired'
}

export interface ContractFile {
  id: string;
  contractId: string;
  fileName: string;
  originalName: string;
  fileSize: number;
  mimeType: string;
  category: FileCategory;
  uploadedAt: Date;
  uploadedBy: string;
  version: number;
  isLatest: boolean;
  checksum: string;
  downloadUrl: string;
  previewUrl?: string;
}

export enum FileCategory {
  CONTRACT = 'contract',
  AMENDMENT = 'amendment',
  SUPPORTING_DOCUMENT = 'supporting_document',
  EVIDENCE = 'evidence',
  CORRESPONDENCE = 'correspondence'
}

export interface ContractMetadata {
  id: string;
  contractId: string;
  extractedData: ExtractedData;
  manualOverrides: ManualOverrides;
  confidenceScores: ConfidenceScores;
  extractedAt: Date;
  extractedBy: string;
  reviewedAt?: Date;
  reviewedBy?: string;
  isReviewed: boolean;
}

export interface ExtractedData {
  parties: ContractParty[];
  keyDates: KeyDate[];
  financialTerms: FinancialTerm[];
  obligations: ExtractedObligation[];
  penalties: Penalty[];
  warranties: Warranty[];
  deliverables: Deliverable[];
  milestones: Milestone[];
}

export interface ContractParty {
  name: string;
  role: string;
  address?: string;
  contactPerson?: string;
  email?: string;
  phone?: string;
}

export interface KeyDate {
  type: string;
  date: Date;
  description: string;
  isRecurring?: boolean;
  frequency?: string;
}

export interface FinancialTerm {
  type: string;
  amount: number;
  currency: string;
  description: string;
  dueDate?: Date;
}

export interface ExtractedObligation {
  description: string;
  responsibleParty: string;
  dueDate?: Date;
  frequency?: string;
  category: string;
  priority: ObligationPriority;
  penalty?: string;
}

export interface Penalty {
  description: string;
  amount?: number;
  percentage?: number;
  currency?: string;
  triggerCondition: string;
  applicableDate?: Date;
}

export interface Warranty {
  description: string;
  startDate: Date;
  endDate: Date;
  coverage: string;
}

export interface Deliverable {
  name: string;
  description: string;
  dueDate: Date;
  responsibleParty: string;
  acceptanceCriteria?: string;
}

export interface Milestone {
  name: string;
  description: string;
  dueDate: Date;
  dependencies?: string[];
  completionCriteria: string;
}

export interface ManualOverrides {
  [key: string]: any;
}

export interface ConfidenceScores {
  overall: number;
  parties: number;
  dates: number;
  obligations: number;
  financial: number;
}

// Obligation model (referenced above)
export interface Obligation {
  id: string;
  contractId: string;
  contractTitle: string;
  projectId: string;
  projectName: string;
  title: string;
  description: string;
  category: ObligationCategory;
  priority: ObligationPriority;
  status: ObligationStatus;
  assignedTo?: string;
  assignedToName?: string;
  dueDate?: Date;
  completedDate?: Date;
  progress: number;
  evidenceFiles: EvidenceFile[];
  comments: ObligationComment[];
  isRecurring: boolean;
  frequency?: RecurrenceFrequency;
  nextDueDate?: Date;
  penaltyAmount?: number;
  penaltyCurrency?: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  updatedBy?: string;
}

export enum ObligationCategory {
  COMPLIANCE = 'compliance',
  DELIVERABLE = 'deliverable',
  REPORTING = 'reporting',
  PAYMENT = 'payment',
  MAINTENANCE = 'maintenance',
  INSURANCE = 'insurance',
  WARRANTY = 'warranty',
  OTHER = 'other'
}

export enum ObligationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ObligationStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled'
}

export enum RecurrenceFrequency {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  SEMI_ANNUALLY = 'semi_annually',
  ANNUALLY = 'annually'
}

export interface EvidenceFile {
  id: string;
  obligationId: string;
  fileName: string;
  originalName: string;
  fileSize: number;
  mimeType: string;
  uploadedAt: Date;
  uploadedBy: string;
  uploadedByName: string;
  description?: string;
  downloadUrl: string;
  previewUrl?: string;
}

export interface ObligationComment {
  id: string;
  obligationId: string;
  userId: string;
  userName: string;
  comment: string;
  timestamp: Date;
  isInternal: boolean;
}