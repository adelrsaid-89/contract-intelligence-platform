import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { DOCUMENT } from '@angular/common';
import { Inject } from '@angular/core';

import { Language } from '@core/models';
import { StorageService } from './storage.service';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private readonly LANGUAGE_KEY = 'selected_language';
  private readonly DIRECTION_KEY = 'text_direction';

  private availableLanguages: Language[] = [
    {
      code: 'en',
      name: 'English',
      flag: '🇺🇸',
      direction: 'ltr'
    },
    {
      code: 'ar',
      name: 'العربية',
      flag: '🇸🇦',
      direction: 'rtl'
    }
  ];

  private currentLanguageSubject = new BehaviorSubject<Language>(this.availableLanguages[0]);
  private availableLanguagesSubject = new BehaviorSubject<Language[]>(this.availableLanguages);

  public currentLanguage$ = this.currentLanguageSubject.asObservable();
  public availableLanguages$ = this.availableLanguagesSubject.asObservable();

  constructor(
    private storageService: StorageService,
    @Inject(DOCUMENT) private document: Document
  ) {}

  initialize(): void {
    const savedLanguageCode = this.storageService.getItem<string>(this.LANGUAGE_KEY);
    const savedDirection = this.storageService.getItem<string>(this.DIRECTION_KEY);

    if (savedLanguageCode) {
      const language = this.availableLanguages.find(lang => lang.code === savedLanguageCode);
      if (language) {
        this.setLanguage(language.code);
      }
    }

    if (savedDirection) {
      this.setDirection(savedDirection as 'ltr' | 'rtl');
    }
  }

  setLanguage(languageCode: string): void {
    const language = this.availableLanguages.find(lang => lang.code === languageCode);
    if (!language) {
      return;
    }

    this.currentLanguageSubject.next(language);
    this.storageService.setItem(this.LANGUAGE_KEY, languageCode);

    // Set HTML lang attribute
    this.document.documentElement.lang = languageCode;

    // Set direction based on language
    this.setDirection(language.direction);

    // Reload the page to apply language changes (for i18n)
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  }

  getCurrentLanguage(): Language {
    return this.currentLanguageSubject.value;
  }

  setDirection(direction: 'ltr' | 'rtl'): void {
    this.document.documentElement.dir = direction;
    this.document.body.className = this.document.body.className.replace(/\b(ltr|rtl)\b/g, '');
    this.document.body.classList.add(direction);

    this.storageService.setItem(this.DIRECTION_KEY, direction);
  }

  getDirection(): 'ltr' | 'rtl' {
    return this.document.documentElement.dir as 'ltr' | 'rtl' || 'ltr';
  }

  toggleDirection(): void {
    const currentDirection = this.getDirection();
    const newDirection = currentDirection === 'ltr' ? 'rtl' : 'ltr';
    this.setDirection(newDirection);
  }

  isRTL(): boolean {
    return this.getDirection() === 'rtl';
  }
}