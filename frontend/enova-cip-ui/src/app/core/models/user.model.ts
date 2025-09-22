export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  projectIds: string[];
  permissions: Permission[];
  profileImage?: string;
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  SUBCONTRACTOR = 'subcontractor'
}

export interface Permission {
  id: string;
  name: string;
  resource: string;
  actions: string[];
}

export interface UserProfile {
  user: User;
  preferences: UserPreferences;
}

export interface UserPreferences {
  language: string;
  theme: string;
  timezone: string;
  dateFormat: string;
  notificationSettings: NotificationSettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  obligationReminders: boolean;
  contractUpdates: boolean;
  systemAlerts: boolean;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  user: User;
  token: AuthToken;
}