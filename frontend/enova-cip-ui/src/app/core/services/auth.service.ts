import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, timer } from 'rxjs';
import { map, catchError, tap, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { jwtDecode } from 'jwt-decode';

import { User, LoginRequest, LoginResponse, AuthToken, UserRole } from '@core/models';
import { StorageService } from './storage.service';
import { environment } from '@environments/environment';

interface JwtPayload {
  sub: string;
  email: string;
  role: UserRole;
  exp: number;
  iat: number;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly API_URL = `${environment.apiUrl}/auth`;
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'current_user';

  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  private tokenRefreshTimer: any;

  public currentUser$ = this.currentUserSubject.asObservable();
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router,
    private storageService: StorageService
  ) {
    this.initializeAuth();
  }

  private initializeAuth(): void {
    const token = this.getToken();
    const user = this.getCurrentUser();

    if (token && user && this.isTokenValid(token)) {
      this.currentUserSubject.next(user);
      this.isAuthenticatedSubject.next(true);
      this.scheduleTokenRefresh();
    } else {
      this.logout();
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/login`, credentials)
      .pipe(
        tap(response => {
          this.setToken(response.token.accessToken);
          this.setRefreshToken(response.token.refreshToken);
          this.setCurrentUser(response.user);
          this.currentUserSubject.next(response.user);
          this.isAuthenticatedSubject.next(true);
          this.scheduleTokenRefresh();
        }),
        catchError(this.handleError)
      );
  }

  logout(): void {
    this.clearTokenRefreshTimer();

    // Call logout endpoint to invalidate token on server
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      this.http.post(`${this.API_URL}/logout`, { refreshToken }).subscribe();
    }

    this.clearAuth();
    this.router.navigate(['/auth/login']);
  }

  refreshToken(): Observable<AuthToken> {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      this.logout();
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post<AuthToken>(`${this.API_URL}/refresh`, { refreshToken })
      .pipe(
        tap(token => {
          this.setToken(token.accessToken);
          this.setRefreshToken(token.refreshToken);
          this.scheduleTokenRefresh();
        }),
        catchError(error => {
          this.logout();
          return throwError(() => error);
        })
      );
  }

  getCurrentUser(): User | null {
    return this.storageService.getItem(this.USER_KEY);
  }

  getToken(): string | null {
    return this.storageService.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return this.storageService.getItem(this.REFRESH_TOKEN_KEY);
  }

  hasRole(role: UserRole): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  hasAnyRole(roles: UserRole[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    return user?.permissions.some(p => p.name === permission) || false;
  }

  canAccessProject(projectId: string): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;

    // Admins can access all projects
    if (user.role === UserRole.ADMIN) return true;

    // Check if user has access to specific project
    return user.projectIds.includes(projectId);
  }

  private setToken(token: string): void {
    this.storageService.setItem(this.TOKEN_KEY, token);
  }

  private setRefreshToken(token: string): void {
    this.storageService.setItem(this.REFRESH_TOKEN_KEY, token);
  }

  private setCurrentUser(user: User): void {
    this.storageService.setItem(this.USER_KEY, user);
  }

  private clearAuth(): void {
    this.storageService.removeItem(this.TOKEN_KEY);
    this.storageService.removeItem(this.REFRESH_TOKEN_KEY);
    this.storageService.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }

  private isTokenValid(token: string): boolean {
    try {
      const payload: JwtPayload = jwtDecode(token);
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  private getTokenExpirationTime(token: string): number {
    try {
      const payload: JwtPayload = jwtDecode(token);
      return payload.exp * 1000;
    } catch {
      return 0;
    }
  }

  private scheduleTokenRefresh(): void {
    this.clearTokenRefreshTimer();

    const token = this.getToken();
    if (!token) return;

    const expirationTime = this.getTokenExpirationTime(token);
    const refreshTime = expirationTime - (5 * 60 * 1000); // Refresh 5 minutes before expiry
    const timeUntilRefresh = refreshTime - Date.now();

    if (timeUntilRefresh > 0) {
      this.tokenRefreshTimer = timer(timeUntilRefresh).subscribe(() => {
        this.refreshToken().subscribe({
          error: () => this.logout()
        });
      });
    } else {
      // Token is about to expire or already expired
      this.refreshToken().subscribe({
        error: () => this.logout()
      });
    }
  }

  private clearTokenRefreshTimer(): void {
    if (this.tokenRefreshTimer) {
      this.tokenRefreshTimer.unsubscribe();
      this.tokenRefreshTimer = null;
    }
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      switch (error.status) {
        case 401:
          errorMessage = 'Invalid credentials';
          break;
        case 403:
          errorMessage = 'Access forbidden';
          break;
        case 404:
          errorMessage = 'Service not found';
          break;
        case 500:
          errorMessage = 'Internal server error';
          break;
        default:
          errorMessage = error.error?.message || `Error Code: ${error.status}`;
      }
    }

    return throwError(() => new Error(errorMessage));
  }
}