import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, timer } from 'rxjs';
import { map, tap } from 'rxjs/operators';

import { Notification, ApiResponse } from '@core/models';
import { environment } from '@environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private readonly API_URL = `${environment.apiUrl}/notifications`;
  private readonly POLL_INTERVAL = 30000; // 30 seconds

  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  private unreadCountSubject = new BehaviorSubject<number>(0);

  public notifications$ = this.notificationsSubject.asObservable();
  public unreadCount$ = this.unreadCountSubject.asObservable();

  constructor(private http: HttpClient) {
    this.startPolling();
  }

  loadNotifications(): Observable<Notification[]> {
    return this.http.get<ApiResponse<Notification[]>>(`${this.API_URL}`)
      .pipe(
        map(response => response.data),
        tap(notifications => {
          this.notificationsSubject.next(notifications);
          this.updateUnreadCount(notifications);
        })
      );
  }

  markAsRead(notificationId: string): Observable<void> {
    return this.http.patch<void>(`${this.API_URL}/${notificationId}/read`, {})
      .pipe(
        tap(() => {
          const notifications = this.notificationsSubject.value;
          const updatedNotifications = notifications.map(n =>
            n.id === notificationId ? { ...n, isRead: true, readAt: new Date() } : n
          );
          this.notificationsSubject.next(updatedNotifications);
          this.updateUnreadCount(updatedNotifications);
        })
      );
  }

  markAllAsRead(): Observable<void> {
    return this.http.patch<void>(`${this.API_URL}/read-all`, {})
      .pipe(
        tap(() => {
          const notifications = this.notificationsSubject.value;
          const updatedNotifications = notifications.map(n => ({ ...n, isRead: true, readAt: new Date() }));
          this.notificationsSubject.next(updatedNotifications);
          this.updateUnreadCount(updatedNotifications);
        })
      );
  }

  deleteNotification(notificationId: string): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${notificationId}`)
      .pipe(
        tap(() => {
          const notifications = this.notificationsSubject.value;
          const updatedNotifications = notifications.filter(n => n.id !== notificationId);
          this.notificationsSubject.next(updatedNotifications);
          this.updateUnreadCount(updatedNotifications);
        })
      );
  }

  private startPolling(): void {
    timer(0, this.POLL_INTERVAL).subscribe(() => {
      this.loadNotifications().subscribe();
    });
  }

  private updateUnreadCount(notifications: Notification[]): void {
    const unreadCount = notifications.filter(n => !n.isRead).length;
    this.unreadCountSubject.next(unreadCount);
  }
}