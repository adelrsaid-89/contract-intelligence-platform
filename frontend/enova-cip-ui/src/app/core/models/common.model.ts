export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: ApiError[];
  meta?: PaginationMeta;
}

export interface ApiError {
  field?: string;
  message: string;
  code?: string;
}

export interface PaginationMeta {
  currentPage: number;
  perPage: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

export interface PaginationRequest {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  search?: string;
  filters?: FilterCriteria[];
}

export interface FilterCriteria {
  field: string;
  operator: FilterOperator;
  value: any;
}

export enum FilterOperator {
  EQUALS = 'eq',
  NOT_EQUALS = 'neq',
  GREATER_THAN = 'gt',
  GREATER_THAN_OR_EQUAL = 'gte',
  LESS_THAN = 'lt',
  LESS_THAN_OR_EQUAL = 'lte',
  CONTAINS = 'contains',
  STARTS_WITH = 'startsWith',
  ENDS_WITH = 'endsWith',
  IN = 'in',
  NOT_IN = 'notIn',
  IS_NULL = 'isNull',
  IS_NOT_NULL = 'isNotNull'
}

export interface DropdownOption {
  label: string;
  value: any;
  disabled?: boolean;
  icon?: string;
  description?: string;
}

export interface TableColumn {
  field: string;
  header: string;
  width?: string;
  sortable?: boolean;
  filterable?: boolean;
  type?: 'text' | 'number' | 'date' | 'boolean' | 'currency' | 'percentage' | 'status' | 'action';
  format?: string;
  visible?: boolean;
  sticky?: boolean;
}

export interface SearchResult {
  id: string;
  type: 'contract' | 'obligation' | 'project';
  title: string;
  description: string;
  url: string;
  relevanceScore: number;
  highlightedText?: string;
  metadata?: any;
}

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  isRead: boolean;
  priority: NotificationPriority;
  actionUrl?: string;
  actionText?: string;
  entityType?: string;
  entityId?: string;
  createdAt: Date;
  readAt?: Date;
  expiresAt?: Date;
}

export enum NotificationType {
  OBLIGATION_DUE = 'obligation_due',
  OBLIGATION_OVERDUE = 'obligation_overdue',
  CONTRACT_EXPIRING = 'contract_expiring',
  DOCUMENT_UPLOADED = 'document_uploaded',
  ASSIGNMENT_CREATED = 'assignment_created',
  SYSTEM_ALERT = 'system_alert',
  REMINDER = 'reminder'
}

export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

export interface FileUpload {
  id: string;
  file: File;
  progress: number;
  status: UploadStatus;
  error?: string;
  url?: string;
}

export enum UploadStatus {
  PENDING = 'pending',
  UPLOADING = 'uploading',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface DashboardWidget {
  id: string;
  title: string;
  type: WidgetType;
  data: any;
  config: WidgetConfig;
  position: WidgetPosition;
}

export enum WidgetType {
  KPI = 'kpi',
  CHART = 'chart',
  TABLE = 'table',
  LIST = 'list',
  CALENDAR = 'calendar',
  MAP = 'map'
}

export interface WidgetConfig {
  refreshInterval?: number;
  dateRange?: DateRange;
  filters?: FilterCriteria[];
  chartType?: string;
  showLegend?: boolean;
  showGrid?: boolean;
}

export interface WidgetPosition {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DateRange {
  start: Date;
  end: Date;
}

export interface BreadcrumbItem {
  label: string;
  url?: string;
  icon?: string;
}

export interface MenuItem {
  label: string;
  icon?: string;
  url?: string;
  children?: MenuItem[];
  permission?: string;
  badge?: string;
  disabled?: boolean;
}

export interface Theme {
  name: string;
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  textColor: string;
  isDark: boolean;
}

export interface Language {
  code: string;
  name: string;
  flag: string;
  direction: 'ltr' | 'rtl';
}