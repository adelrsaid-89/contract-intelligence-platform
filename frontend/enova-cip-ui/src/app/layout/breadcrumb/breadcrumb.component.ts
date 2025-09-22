import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { filter, takeUntil } from 'rxjs/operators';

import { BreadcrumbItem } from '@core/models';

@Component({
  selector: 'app-breadcrumb',
  templateUrl: './breadcrumb.component.html',
  styleUrls: ['./breadcrumb.component.scss']
})
export class BreadcrumbComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  breadcrumbs: BreadcrumbItem[] = [];

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe(() => {
        this.breadcrumbs = this.createBreadcrumbs(this.activatedRoute.root);
      });

    // Initial breadcrumbs
    this.breadcrumbs = this.createBreadcrumbs(this.activatedRoute.root);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private createBreadcrumbs(route: ActivatedRoute, url = '', breadcrumbs: BreadcrumbItem[] = []): BreadcrumbItem[] {
    const children: ActivatedRoute[] = route.children;

    if (children.length === 0) {
      return breadcrumbs;
    }

    for (const child of children) {
      const routeURL: string = child.snapshot.url.map(segment => segment.path).join('/');
      if (routeURL !== '') {
        url += `/${routeURL}`;
      }

      const breadcrumbData = child.snapshot.data['breadcrumb'];
      if (breadcrumbData) {
        const breadcrumb: BreadcrumbItem = {
          label: this.resolveBreadcrumbLabel(breadcrumbData, child),
          url: url,
          icon: child.snapshot.data['breadcrumbIcon']
        };
        breadcrumbs.push(breadcrumb);
      }

      return this.createBreadcrumbs(child, url, breadcrumbs);
    }

    return breadcrumbs;
  }

  private resolveBreadcrumbLabel(breadcrumbData: any, route: ActivatedRoute): string {
    if (typeof breadcrumbData === 'function') {
      return breadcrumbData(route.snapshot);
    }

    if (typeof breadcrumbData === 'string') {
      // Check if it's a parameter reference
      const paramMatch = breadcrumbData.match(/\{\{(\w+)\}\}/);
      if (paramMatch) {
        const paramName = paramMatch[1];
        return route.snapshot.params[paramName] || route.snapshot.data[paramName] || breadcrumbData;
      }
      return breadcrumbData;
    }

    return breadcrumbData?.toString() || '';
  }

  onBreadcrumbClick(breadcrumb: BreadcrumbItem): void {
    if (breadcrumb.url) {
      this.router.navigate([breadcrumb.url]);
    }
  }
}