import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Observable } from 'rxjs';
import { filter } from 'rxjs/operators';

import { AuthService } from '@core/services/auth.service';
import { User, UserRole, MenuItem } from '@core/models';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  @Input() user: User | null = null;
  @Input() isCollapsed = false;
  @Output() menuItemClicked = new EventEmitter<void>();

  currentRoute = '';
  menuItems: MenuItem[] = [];

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.buildMenu();
    this.trackCurrentRoute();
  }

  private buildMenu(): void {
    const userRole = this.user?.role;

    this.menuItems = [
      {
        label: 'Dashboard',
        icon: 'dashboard',
        url: '/dashboard'
      },
      {
        label: 'Projects',
        icon: 'folder',
        url: '/projects',
        permission: 'view_projects'
      },
      {
        label: 'Contracts',
        icon: 'description',
        url: '/contracts',
        children: [
          {
            label: 'All Contracts',
            icon: 'list',
            url: '/contracts'
          },
          {
            label: 'Upload Contract',
            icon: 'upload_file',
            url: '/contracts/upload',
            permission: 'upload_contracts'
          }
        ]
      },
      {
        label: 'Obligations',
        icon: 'assignment',
        url: '/obligations',
        children: [
          {
            label: 'My Tasks',
            icon: 'task',
            url: '/obligations/my-tasks'
          },
          {
            label: 'All Obligations',
            icon: 'list',
            url: '/obligations',
            permission: 'view_all_obligations'
          },
          {
            label: 'Kanban Board',
            icon: 'view_column',
            url: '/obligations/kanban'
          },
          {
            label: 'Calendar View',
            icon: 'calendar_month',
            url: '/obligations/calendar'
          }
        ]
      },
      {
        label: 'AI Assistant',
        icon: 'psychology',
        url: '/ai',
        children: [
          {
            label: 'Q&A Console',
            icon: 'chat',
            url: '/ai/qa'
          },
          {
            label: 'Document Analysis',
            icon: 'analytics',
            url: '/ai/analysis',
            permission: 'use_ai_analysis'
          }
        ]
      },
      {
        label: 'Search',
        icon: 'search',
        url: '/search'
      },
      {
        label: 'Reports',
        icon: 'assessment',
        url: '/reports',
        permission: 'view_reports',
        children: [
          {
            label: 'Compliance Reports',
            icon: 'rule',
            url: '/reports/compliance'
          },
          {
            label: 'Performance Reports',
            icon: 'trending_up',
            url: '/reports/performance'
          },
          {
            label: 'Risk Analysis',
            icon: 'warning',
            url: '/reports/risk'
          }
        ]
      }
    ];

    // Admin-only items
    if (userRole === UserRole.ADMIN) {
      this.menuItems.push({
        label: 'Administration',
        icon: 'admin_panel_settings',
        url: '/admin',
        children: [
          {
            label: 'User Management',
            icon: 'people',
            url: '/admin/users'
          },
          {
            label: 'System Settings',
            icon: 'settings',
            url: '/admin/settings'
          },
          {
            label: 'Audit Logs',
            icon: 'history',
            url: '/admin/audit-logs'
          }
        ]
      });
    }

    // Filter menu items based on permissions
    this.menuItems = this.filterMenuItems(this.menuItems);
  }

  private filterMenuItems(items: MenuItem[]): MenuItem[] {
    return items.filter(item => {
      // Check permission if specified
      if (item.permission && !this.authService.hasPermission(item.permission)) {
        return false;
      }

      // Filter children if they exist
      if (item.children) {
        item.children = this.filterMenuItems(item.children);
        // Hide parent if no children are visible
        return item.children.length > 0;
      }

      return true;
    });
  }

  private trackCurrentRoute(): void {
    this.currentRoute = this.router.url;

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.currentRoute = event.url;
      });
  }

  onMenuItemClick(item: MenuItem): void {
    if (item.url && !item.children?.length) {
      this.router.navigate([item.url]);
      this.menuItemClicked.emit();
    }
  }

  isMenuItemActive(item: MenuItem): boolean {
    if (!item.url) return false;

    if (item.children?.length) {
      return item.children.some(child => this.isMenuItemActive(child));
    }

    return this.currentRoute === item.url || this.currentRoute.startsWith(item.url + '/');
  }

  isMenuItemExpanded(item: MenuItem): boolean {
    if (!item.children?.length) return false;
    return item.children.some(child => this.isMenuItemActive(child));
  }
}