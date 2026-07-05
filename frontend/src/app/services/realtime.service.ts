import { Injectable, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RealtimeEvent {
  type: string;
  data: unknown;
}

@Injectable({ providedIn: 'root' })
export class RealtimeService implements OnDestroy {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private _events$ = new Subject<RealtimeEvent>();
  private _retryDelay = 1000;

  readonly events$ = this._events$.asObservable();

  connect(): void {
    if (this.ws) return;
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = environment.wsUrl || `${proto}://${window.location.host}/ws`;
    if (!url) return;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this._retryDelay = 1000; // reset backoff on successful connection
    };

    this.ws.onmessage = (e) => {
      try {
        const parsed = JSON.parse(e.data) as RealtimeEvent;
        this._events$.next(parsed);
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
      this.reconnectTimer = setTimeout(() => this.connect(), this._retryDelay);
      this._retryDelay = Math.min(this._retryDelay * 2, 30_000);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  ngOnDestroy(): void {
    this.disconnect();
    this._events$.complete();
  }
}
