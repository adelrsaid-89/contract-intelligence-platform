import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationStart, NavigationEnd, NavigationCancel, NavigationError } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil, filter } from 'rxjs/operators';

import { AuthService } from '@core/services/auth.service';
import { LanguageService } from '@core/services/language.service';
import { ThemeService } from '@core/services/theme.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  title = 'Contract Intelligence Platform';
  isLoading = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private languageService: LanguageService,
    private themeService: ThemeService
  ) {}

  ngOnInit(): void {
    this.initializeApp();
    this.setupRouterLoadingIndicator();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initializeApp(): void {
    // Initialize language service
    this.languageService.initialize();

    // Initialize theme service
    this.themeService.initialize();

    // Initialize authentication
    // AuthService initialization happens in constructor
  }

  private setupRouterLoadingIndicator(): void {
    this.router.events
      .pipe(takeUntil(this.destroy$))
      .subscribe(event => {
        if (event instanceof NavigationStart) {
          this.isLoading = true;
        } else if (
          event instanceof NavigationEnd ||
          event instanceof NavigationCancel ||
          event instanceof NavigationError
        ) {
          this.isLoading = false;
        }
      });
  }
}