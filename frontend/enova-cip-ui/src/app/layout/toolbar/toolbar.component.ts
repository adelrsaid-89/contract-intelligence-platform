import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';

import { AuthService } from '@core/services/auth.service';
import { NotificationService } from '@core/services/notification.service';
import { LanguageService } from '@core/services/language.service';
import { User, Notification, Language } from '@core/models';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent implements OnInit {
  @Input() user: User | null = null;
  @Input() isMobile = false;
  @Input() isSidenavOpen = true;
  @Output() toggleSidenav = new EventEmitter<void>();

  notifications$: Observable<Notification[]>;
  unreadNotificationCount$: Observable<number>;
  currentLanguage$: Observable<Language>;
  availableLanguages$: Observable<Language[]>;

  searchQuery = '';

  constructor(
    private authService: AuthService,
    private notificationService: NotificationService,
    private languageService: LanguageService,
    private router: Router
  ) {
    this.notifications$ = this.notificationService.notifications$;
    this.unreadNotificationCount$ = this.notificationService.unreadCount$;
    this.currentLanguage$ = this.languageService.currentLanguage$;
    this.availableLanguages$ = this.languageService.availableLanguages$;
  }

  ngOnInit(): void {
    // Load notifications
    this.notificationService.loadNotifications();
  }

  onToggleSidenav(): void {
    this.toggleSidenav.emit();
  }

  onSearch(): void {
    if (this.searchQuery.trim()) {
      this.router.navigate(['/search'], {
        queryParams: { q: this.searchQuery.trim() }
      });
    }
  }

  onLanguageChange(language: Language): void {
    this.languageService.setLanguage(language.code);
  }

  onToggleRTL(): void {
    this.languageService.toggleDirection();
  }

  onNotificationClick(notification: Notification): void {
    this.notificationService.markAsRead(notification.id);

    if (notification.actionUrl) {
      this.router.navigate([notification.actionUrl]);
    }
  }

  onMarkAllNotificationsRead(): void {
    this.notificationService.markAllAsRead();
  }

  onViewAllNotifications(): void {
    this.router.navigate(['/notifications']);
  }

  onProfile(): void {
    this.router.navigate(['/profile']);
  }

  onSettings(): void {
    this.router.navigate(['/settings']);
  }

  onLogout(): void {
    this.authService.logout();
  }

  getNotificationIcon(type: string): string {
    const iconMap: { [key: string]: string } = {
      'obligation_due': 'schedule',
      'obligation_overdue': 'warning',
      'contract_expiring': 'event_busy',
      'document_uploaded': 'upload_file',
      'assignment_created': 'assignment',
      'system_alert': 'info',
      'reminder': 'notifications'
    };

    return iconMap[type] || 'notifications';
  }

  getNotificationColor(priority: string): string {
    const colorMap: { [key: string]: string } = {
      'low': '',
      'medium': 'accent',
      'high': 'warn',
      'urgent': 'warn'
    };

    return colorMap[priority] || '';
  }

  formatNotificationTime(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - new Date(date).getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return new Date(date).toLocaleDateString();
    }
  }
}