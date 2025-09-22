import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { DOCUMENT } from '@angular/common';
import { Inject } from '@angular/core';

import { Theme } from '@core/models';
import { StorageService } from './storage.service';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'selected_theme';

  private availableThemes: Theme[] = [
    {
      name: 'light',
      primaryColor: '#3f51b5',
      accentColor: '#ff4081',
      backgroundColor: '#fafafa',
      textColor: '#212121',
      isDark: false
    },
    {
      name: 'dark',
      primaryColor: '#3f51b5',
      accentColor: '#ff4081',
      backgroundColor: '#303030',
      textColor: '#ffffff',
      isDark: true
    }
  ];

  private currentThemeSubject = new BehaviorSubject<Theme>(this.availableThemes[0]);

  public currentTheme$ = this.currentThemeSubject.asObservable();

  constructor(
    private storageService: StorageService,
    @Inject(DOCUMENT) private document: Document
  ) {}

  initialize(): void {
    const savedThemeName = this.storageService.getItem<string>(this.THEME_KEY);

    if (savedThemeName) {
      const theme = this.availableThemes.find(t => t.name === savedThemeName);
      if (theme) {
        this.setTheme(theme);
      }
    } else {
      // Check system preference
      if (this.prefersDarkMode()) {
        this.setTheme(this.availableThemes[1]); // dark theme
      } else {
        this.setTheme(this.availableThemes[0]); // light theme
      }
    }
  }

  setTheme(theme: Theme): void {
    this.currentThemeSubject.next(theme);
    this.storageService.setItem(this.THEME_KEY, theme.name);

    // Update CSS classes
    this.document.body.className = this.document.body.className.replace(/\b(light-theme|dark-theme)\b/g, '');
    this.document.body.classList.add(`${theme.name}-theme`);

    // Update CSS custom properties
    const root = this.document.documentElement;
    root.style.setProperty('--primary-color', theme.primaryColor);
    root.style.setProperty('--accent-color', theme.accentColor);
    root.style.setProperty('--background-color', theme.backgroundColor);
    root.style.setProperty('--text-color', theme.textColor);
  }

  getCurrentTheme(): Theme {
    return this.currentThemeSubject.value;
  }

  toggleTheme(): void {
    const currentTheme = this.getCurrentTheme();
    const newTheme = currentTheme.name === 'light' ? this.availableThemes[1] : this.availableThemes[0];
    this.setTheme(newTheme);
  }

  isDarkMode(): boolean {
    return this.getCurrentTheme().isDark;
  }

  private prefersDarkMode(): boolean {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  }
}