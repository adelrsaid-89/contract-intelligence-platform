import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable, Subject } from 'rxjs';
import { map, shareReplay, takeUntil } from 'rxjs/operators';

import { AuthService } from '@core/services/auth.service';
import { User } from '@core/models';

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.scss']
})
export class MainLayoutComponent implements OnInit, OnDestroy {
  @ViewChild('drawer') drawer!: MatSidenav;

  private destroy$ = new Subject<void>();

  currentUser$: Observable<User | null>;
  isHandset$: Observable<boolean>;
  isSidenavOpen = true;

  constructor(
    private breakpointObserver: BreakpointObserver,
    private authService: AuthService
  ) {
    this.currentUser$ = this.authService.currentUser$;
    this.isHandset$ = this.breakpointObserver.observe(Breakpoints.Handset)
      .pipe(
        map(result => result.matches),
        shareReplay()
      );
  }

  ngOnInit(): void {
    // Auto-close sidebar on mobile
    this.isHandset$
      .pipe(takeUntil(this.destroy$))
      .subscribe(isHandset => {
        if (isHandset) {
          this.isSidenavOpen = false;
        } else {
          this.isSidenavOpen = true;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  toggleSidenav(): void {
    if (this.drawer) {
      this.drawer.toggle();
    } else {
      this.isSidenavOpen = !this.isSidenavOpen;
    }
  }

  onSidenavClosed(): void {
    this.isSidenavOpen = false;
  }

  onSidenavOpened(): void {
    this.isSidenavOpen = true;
  }
}