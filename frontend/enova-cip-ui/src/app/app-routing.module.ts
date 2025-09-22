import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { AuthGuard } from '@core/guards/auth.guard';
import { RoleGuard } from '@core/guards/role.guard';
import { UserRole } from '@core/models';

const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.module').then(m => m.AuthModule),
    data: {
      breadcrumb: 'Authentication'
    }
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () => import('./features/dashboard/dashboard.module').then(m => m.DashboardModule),
        data: {
          breadcrumb: 'Dashboard',
          breadcrumbIcon: 'dashboard'
        }
      },
      {
        path: 'projects',
        loadChildren: () => import('./features/projects/projects.module').then(m => m.ProjectsModule),
        canActivate: [RoleGuard],
        data: {
          breadcrumb: 'Projects',
          breadcrumbIcon: 'folder',
          roles: [UserRole.ADMIN, UserRole.MANAGER]
        }
      },
      {
        path: 'contracts',
        loadChildren: () => import('./features/contracts/contracts.module').then(m => m.ContractsModule),
        data: {
          breadcrumb: 'Contracts',
          breadcrumbIcon: 'description'
        }
      },
      {
        path: 'obligations',
        loadChildren: () => import('./features/obligations/obligations.module').then(m => m.ObligationsModule),
        data: {
          breadcrumb: 'Obligations',
          breadcrumbIcon: 'assignment'
        }
      },
      {
        path: 'ai',
        loadChildren: () => import('./features/ai/ai.module').then(m => m.AiModule),
        data: {
          breadcrumb: 'AI Assistant',
          breadcrumbIcon: 'psychology'
        }
      },
      {
        path: 'search',
        loadChildren: () => import('./features/search/search.module').then(m => m.SearchModule),
        data: {
          breadcrumb: 'Search',
          breadcrumbIcon: 'search'
        }
      },
      {
        path: 'reports',
        loadChildren: () => import('./features/reports/reports.module').then(m => m.ReportsModule),
        canActivate: [RoleGuard],
        data: {
          breadcrumb: 'Reports',
          breadcrumbIcon: 'assessment',
          permissions: ['view_reports']
        }
      },
      {
        path: 'admin',
        loadChildren: () => import('./features/admin/admin.module').then(m => m.AdminModule),
        canActivate: [RoleGuard],
        data: {
          breadcrumb: 'Administration',
          breadcrumbIcon: 'admin_panel_settings',
          roles: [UserRole.ADMIN]
        }
      },
      {
        path: 'profile',
        loadChildren: () => import('./features/profile/profile.module').then(m => m.ProfileModule),
        data: {
          breadcrumb: 'Profile',
          breadcrumbIcon: 'person'
        }
      },
      {
        path: 'settings',
        loadChildren: () => import('./features/settings/settings.module').then(m => m.SettingsModule),
        data: {
          breadcrumb: 'Settings',
          breadcrumbIcon: 'settings'
        }
      },
      {
        path: 'notifications',
        loadChildren: () => import('./features/notifications/notifications.module').then(m => m.NotificationsModule),
        data: {
          breadcrumb: 'Notifications',
          breadcrumbIcon: 'notifications'
        }
      }
    ]
  },
  {
    path: 'unauthorized',
    loadChildren: () => import('./features/unauthorized/unauthorized.module').then(m => m.UnauthorizedModule)
  },
  {
    path: '**',
    loadChildren: () => import('./features/not-found/not-found.module').then(m => m.NotFoundModule)
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    enableTracing: false, // Set to true for debugging
    scrollPositionRestoration: 'top',
    anchorScrolling: 'enabled',
    onSameUrlNavigation: 'reload'
  })],
  exports: [RouterModule]
})
export class AppRoutingModule { }