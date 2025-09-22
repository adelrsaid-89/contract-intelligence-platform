import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ToastrService } from 'ngx-toastr';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  constructor(private toastr: ToastrService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        this.handleError(error);
        return throwError(() => error);
      })
    );
  }

  private handleError(error: HttpErrorResponse): void {
    let errorMessage = 'An unexpected error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      switch (error.status) {
        case 400:
          errorMessage = this.extractErrorMessage(error) || 'Bad request';
          break;
        case 401:
          // Handled by AuthInterceptor
          return;
        case 403:
          errorMessage = 'You do not have permission to perform this action';
          break;
        case 404:
          errorMessage = 'The requested resource was not found';
          break;
        case 409:
          errorMessage = this.extractErrorMessage(error) || 'A conflict occurred';
          break;
        case 422:
          errorMessage = this.extractValidationErrors(error) || 'Validation failed';
          break;
        case 500:
          errorMessage = 'Internal server error. Please try again later';
          break;
        case 502:
        case 503:
        case 504:
          errorMessage = 'Service temporarily unavailable. Please try again later';
          break;
        default:
          errorMessage = `Error ${error.status}: ${error.statusText}`;
      }
    }

    // Don't show error toast for certain endpoints or status codes
    if (!this.shouldShowError(error)) {
      return;
    }

    this.toastr.error(errorMessage, 'Error', {
      timeOut: 5000,
      closeButton: true,
      progressBar: true
    });
  }

  private extractErrorMessage(error: HttpErrorResponse): string | null {
    if (error.error?.message) {
      return error.error.message;
    }

    if (error.error?.errors && Array.isArray(error.error.errors)) {
      return error.error.errors[0]?.message || null;
    }

    return null;
  }

  private extractValidationErrors(error: HttpErrorResponse): string | null {
    if (error.error?.errors && Array.isArray(error.error.errors)) {
      const messages = error.error.errors.map((err: any) => err.message || err);
      return messages.join(', ');
    }

    return this.extractErrorMessage(error);
  }

  private shouldShowError(error: HttpErrorResponse): boolean {
    // Don't show errors for specific endpoints
    const silentEndpoints = [
      '/auth/refresh',
      '/notifications/count'
    ];

    const isSilentEndpoint = silentEndpoints.some(endpoint =>
      error.url?.includes(endpoint)
    );

    // Don't show errors for 401 (handled by auth interceptor)
    const isSilentStatus = error.status === 401;

    return !isSilentEndpoint && !isSilentStatus;
  }
}