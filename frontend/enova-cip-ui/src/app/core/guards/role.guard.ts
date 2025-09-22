import { Injectable } from '@angular/core';
import { CanActivate, CanActivateChild, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, map, take } from 'rxjs';

import { AuthService } from '@core/services/auth.service';
import { UserRole } from '@core/models';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate, CanActivateChild {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> {
    return this.checkRole(route);
  }

  canActivateChild(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> {
    return this.checkRole(route);
  }

  private checkRole(route: ActivatedRouteSnapshot): Observable<boolean> {
    const expectedRoles = route.data['roles'] as UserRole[];
    const expectedPermissions = route.data['permissions'] as string[];

    return this.authService.currentUser$.pipe(
      take(1),
      map(user => {
        if (!user) {
          this.router.navigate(['/auth/login']);
          return false;
        }

        // Check roles
        if (expectedRoles && expectedRoles.length > 0) {
          const hasRole = this.authService.hasAnyRole(expectedRoles);
          if (!hasRole) {
            this.router.navigate(['/unauthorized']);
            return false;
          }
        }

        // Check permissions
        if (expectedPermissions && expectedPermissions.length > 0) {
          const hasPermission = expectedPermissions.some(permission =>
            this.authService.hasPermission(permission)
          );
          if (!hasPermission) {
            this.router.navigate(['/unauthorized']);
            return false;
          }
        }

        return true;
      })
    );
  }
}