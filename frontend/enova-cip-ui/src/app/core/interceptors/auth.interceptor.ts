import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';

import { AuthService } from '@core/services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;

  constructor(private authService: AuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip authentication for login and refresh token requests
    if (this.isAuthRequest(req.url)) {
      return next.handle(req);
    }

    const authToken = this.authService.getToken();

    // Add authentication header if token exists
    if (authToken) {
      req = this.addAuthHeader(req, authToken);
    }

    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401 && !this.isAuthRequest(req.url) && !this.isRefreshing) {
          return this.handle401Error(req, next);
        }
        return throwError(() => error);
      })
    );
  }

  private addAuthHeader(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;

      return this.authService.refreshToken().pipe(
        switchMap(tokenResponse => {
          this.isRefreshing = false;
          const newRequest = this.addAuthHeader(request, tokenResponse.accessToken);
          return next.handle(newRequest);
        }),
        catchError(error => {
          this.isRefreshing = false;
          this.authService.logout();
          return throwError(() => error);
        })
      );
    }

    // If we're already refreshing, reject this request
    return throwError(() => new Error('Token refresh in progress'));
  }

  private isAuthRequest(url: string): boolean {
    return url.includes('/auth/login') ||
           url.includes('/auth/refresh') ||
           url.includes('/auth/logout');
  }
}