import { Component, Input, OnInit, OnDestroy, ElementRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { RealtimeService } from '../../services/realtime.service';
import { DomainEvent, EventFilter } from '../../models/event.model';
import { Subscription } from 'rxjs';

const SOURCE_LABELS: Record<string, string> = {
  ui: 'UI', api: 'API', demo: 'Demo', agent: 'Agent', system: 'System',
};

const TOPIC_OPTIONS = [
  'packages', 'package-status', 'package-location',
  'truck-location', 'truck-reroute', 'manager-actions', 'complaints', 'audit-log',
];

@Component({
  selector: 'app-event-stream',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div class="card" role="region" aria-label="Event stream panel">
      <!-- Header row -->
      <div class="flex items-center justify-between mb-2">
        <h2 class="font-semibold text-gray-800 text-sm">Live Events</h2>
        <div class="flex items-center gap-2">
          @if (bufferedCount > 0) {
            <span class="text-xs text-orange-600 font-medium">{{ bufferedCount }} queued</span>
          }
          <button
            (click)="toggleFilters()"
            [attr.aria-expanded]="showFilters"
            aria-controls="event-filter-panel"
            class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-dm-blue focus:outline-none focus:ring-1 focus:ring-dm-blue transition-colors"
            [class.bg-blue-50]="showFilters"
          >
            {{ showFilters ? '▲ Filters' : '▼ Filters' }}
          </button>
          <button
            (click)="clearEvents()"
            aria-label="Clear event display"
            class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-red-300 focus:outline-none focus:ring-1 focus:ring-red-300 transition-colors"
          >
            Clear
          </button>
          <button
            (click)="togglePause()"
            [attr.aria-pressed]="paused"
            class="text-xs px-2 py-0.5 rounded border border-gray-200 hover:border-dm-blue focus:outline-none focus:ring-1 focus:ring-dm-blue transition-colors"
            [class.bg-orange-50]="paused"
            [class.border-orange-300]="paused"
          >
            {{ paused ? '▶ Resume' : '⏸ Pause' }}
          </button>
        </div>
      </div>

      <!-- Collapsible filter panel -->
      @if (showFilters) {
        <div id="event-filter-panel" class="mb-3 p-2 bg-gray-50 rounded border border-gray-200 grid grid-cols-2 gap-2 text-xs">
          <div class="flex flex-col gap-0.5">
            <label for="filter-topic" class="text-gray-500 font-medium">Topic</label>
            <select id="filter-topic" [(ngModel)]="filter.topic" (ngModelChange)="applyFilter()" class="border border-gray-200 rounded px-1 py-0.5 text-xs">
              <option value="">All</option>
              @for (t of topicOptions; track t) {
                <option [value]="t">{{ t }}</option>
              }
            </select>
          </div>
          <div class="flex flex-col gap-0.5">
            <label for="filter-source" class="text-gray-500 font-medium">Source</label>
            <select id="filter-source" [(ngModel)]="filter.source" (ngModelChange)="applyFilter()" class="border border-gray-200 rounded px-1 py-0.5 text-xs">
              <option value="">All</option>
              @for (s of ['ui','api','demo','agent','system']; track s) {
                <option [value]="s">{{ s }}</option>
              }
            </select>
          </div>
          <div class="flex flex-col gap-0.5">
            <label for="filter-entity-id" class="text-gray-500 font-medium">Entity ID</label>
            <input id="filter-entity-id" type="text" [(ngModel)]="filter.entity_id" (ngModelChange)="applyFilter()"
              placeholder="e.g. PKG-2024-001" class="border border-gray-200 rounded px-1 py-0.5 text-xs" />
          </div>
          <div class="flex flex-col gap-0.5">
            <label for="filter-actor" class="text-gray-500 font-medium">Actor ID</label>
            <input id="filter-actor" type="text" [(ngModel)]="filter.actor_id" (ngModelChange)="applyFilter()"
              placeholder="e.g. michael-scott" class="border border-gray-200 rounded px-1 py-0.5 text-xs" />
          </div>
          <div class="flex flex-col gap-0.5 col-span-2">
            <label for="filter-corr" class="text-gray-500 font-medium">Correlation ID</label>
            <input id="filter-corr" type="text" [(ngModel)]="filter.correlation_id" (ngModelChange)="applyFilter()"
              placeholder="UUID" class="border border-gray-200 rounded px-1 py-0.5 text-xs" />
          </div>
          <div class="col-span-2 flex justify-end">
            <button (click)="clearFilter()" class="text-xs text-gray-500 hover:text-gray-800 underline">
              Clear filters
            </button>
          </div>
        </div>
      }

      <!-- Event list -->
      <div
        #streamList
        role="log"
        aria-live="polite"
        aria-label="Event stream"
        aria-atomic="false"
        class="space-y-1.5 max-h-96 overflow-y-auto"
      >
        @if (filteredEvents.length === 0) {
          <p class="text-xs text-gray-400">No events yet.</p>
        } @else {
          @for (e of filteredEvents; track e.event_id) {
            <div class="text-xs border-l-2 pl-2 py-0.5"
              [class.border-dm-blue]="!isExpanded(e)"
              [class.border-indigo-400]="isExpanded(e)">

              <!-- Summary row -->
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="font-semibold text-gray-800">{{ e.event_type }}</span>
                <span class="badge bg-gray-100 text-gray-500 text-xs">{{ sourceLabel(e.source) }}</span>
                <span class="badge text-xs" [class]="topicBadgeClass(e.topic)">{{ e.topic }}</span>

                <!-- Entity navigation link -->
                @if (entityLink(e); as link) {
                  <a [routerLink]="link.path" [queryParams]="link.params"
                    class="text-dm-blue underline hover:no-underline" [attr.aria-label]="'Open ' + e.entity_type + ' ' + e.entity_id">
                    {{ e.entity_type }}/{{ e.entity_id }}
                  </a>
                } @else {
                  <span class="text-gray-400">{{ e.entity_type }}/{{ e.entity_id }}</span>
                }

                <div class="ml-auto flex gap-1">
                  <button (click)="toggleExpand(e)" [attr.aria-label]="isExpanded(e) ? 'Collapse event details' : 'Expand event details'"
                    class="text-gray-400 hover:text-gray-700 focus:outline-none">
                    {{ isExpanded(e) ? '▲' : '▼' }}
                  </button>
                  <button (click)="copyEvent(e)" aria-label="Copy event payload to clipboard"
                    class="text-gray-400 hover:text-gray-700 focus:outline-none">
                    {{ copiedId === e.event_id ? '✓' : '⧉' }}
                  </button>
                </div>
              </div>

              <!-- Human-readable summary -->
              @if (e.summary) {
                <div class="text-gray-600 mt-0.5">{{ e.summary }}</div>
              }

              <!-- Actor + time -->
              <div class="text-gray-400 mt-0.5">
                {{ e.actor.actor_name || 'system' }}
                @if (e.actor.persona) { <span>({{ e.actor.persona }})</span> }
                · {{ relativeTime(e.occurred_at) }}
                @if (e.correlation_id) {
                  · <span class="text-purple-400 font-mono text-xs" [title]="'Correlation ID: ' + e.correlation_id">corr:{{ e.correlation_id.slice(0, 8) }}</span>
                }
              </div>

              <!-- Expanded payload -->
              @if (isExpanded(e)) {
                <div class="mt-1.5 bg-gray-50 rounded p-2 text-xs font-mono whitespace-pre-wrap break-all max-h-48 overflow-y-auto"
                  aria-label="Event payload">{{ formatPayload(e) }}</div>
              }
            </div>
          }
        }
      </div>
    </div>
  `,
})
export class EventStreamComponent implements OnInit, OnDestroy {
  @Input() maxItems = 100;
  @ViewChild('streamList') private streamListRef!: ElementRef<HTMLElement>;

  private api = inject(ApiService);
  private realtime = inject(RealtimeService);
  private sub: Subscription | null = null;

  protected events: DomainEvent[] = [];
  protected filteredEvents: DomainEvent[] = [];
  protected paused = false;
  protected bufferedCount = 0;
  protected showFilters = false;
  protected filter: EventFilter = {};
  protected topicOptions = TOPIC_OPTIONS;
  protected copiedId: string | null = null;

  private buffer: DomainEvent[] = [];
  private expandedIds = new Set<string>();

  ngOnInit(): void {
    this.api.getEvents(Math.min(this.maxItems, 50)).subscribe(es => {
      this.events = es.map(e => this.normalizeEvent(e)).slice(0, this.maxItems);
      this.applyFilter();
    });

    this.sub = this.realtime.events$.subscribe(event => {
      const entry = this.normalizeEvent(event.data ?? event);

      if (this.paused) {
        this.buffer.push(entry);
        this.bufferedCount = this.buffer.length;
      } else {
        this.addEntry(entry);
      }
    });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }

  togglePause(): void {
    this.paused = !this.paused;
    if (!this.paused && this.buffer.length > 0) {
      for (const entry of this.buffer) {
        this.addEntry(entry);
      }
      this.buffer = [];
      this.bufferedCount = 0;
      this.scrollToTop();
    }
  }

  clearEvents(): void {
    this.events = [];
    this.filteredEvents = [];
    this.expandedIds.clear();
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
  }

  applyFilter(): void {
    this.filteredEvents = this.events.filter(e => {
      if (this.filter.topic && e.topic !== this.filter.topic) return false;
      if (this.filter.source && e.source !== this.filter.source) return false;
      if (this.filter.entity_id && !e.entity_id.includes(this.filter.entity_id)) return false;
      if (this.filter.actor_id && !e.actor.actor_id.includes(this.filter.actor_id)) return false;
      if (this.filter.correlation_id && e.correlation_id !== this.filter.correlation_id) return false;
      return true;
    });
  }

  clearFilter(): void {
    this.filter = {};
    this.applyFilter();
  }

  toggleExpand(e: DomainEvent): void {
    if (this.expandedIds.has(e.event_id)) {
      this.expandedIds.delete(e.event_id);
    } else {
      this.expandedIds.add(e.event_id);
    }
  }

  isExpanded(e: DomainEvent): boolean {
    return this.expandedIds.has(e.event_id);
  }

  copyEvent(e: DomainEvent): void {
    const json = JSON.stringify(e, null, 2);
    navigator.clipboard.writeText(json).then(() => {
      this.copiedId = e.event_id;
      setTimeout(() => { if (this.copiedId === e.event_id) this.copiedId = null; }, 1500);
    });
  }

  entityLink(e: DomainEvent): { path: string; params?: Record<string, string> } | null {
    if (e.entity_type === 'package') return { path: `/packages/${e.entity_id}` };
    if (e.entity_type === 'complaint') return { path: `/complaints/${e.entity_id}` };
    if (e.entity_type === 'truck') return { path: '/map', params: { truck: e.entity_id } };
    return null;
  }

  sourceLabel(source: string): string {
    return SOURCE_LABELS[source] ?? source;
  }

  topicBadgeClass(topic: string): string {
    const map: Record<string, string> = {
      'packages': 'bg-blue-50 text-blue-600',
      'package-status': 'bg-green-50 text-green-600',
      'package-location': 'bg-teal-50 text-teal-600',
      'truck-location': 'bg-yellow-50 text-yellow-700',
      'truck-reroute': 'bg-orange-50 text-orange-700',
      'manager-actions': 'bg-purple-50 text-purple-700',
      'complaints': 'bg-red-50 text-red-600',
      'audit-log': 'bg-gray-100 text-gray-600',
    };
    return map[topic] ?? 'bg-gray-100 text-gray-500';
  }

  formatPayload(e: DomainEvent): string {
    return JSON.stringify({
      event_id: e.event_id,
      event_type: e.event_type,
      topic: e.topic,
      occurred_at: e.occurred_at,
      actor: e.actor,
      source: e.source,
      entity_type: e.entity_type,
      entity_id: e.entity_id,
      correlation_id: e.correlation_id,
      payload: e.payload,
      summary: e.summary,
    }, null, 2);
  }

  relativeTime(iso: string): string {
    try {
      const diff = Date.now() - new Date(iso).getTime();
      const mins = Math.floor(diff / 60000);
      if (mins < 1) return 'just now';
      if (mins < 60) return `${mins} min ago`;
      const hrs = Math.floor(mins / 60);
      if (hrs < 24) return `${hrs}h ago`;
      return new Date(iso).toLocaleDateString();
    } catch {
      return iso;
    }
  }

  private addEntry(entry: DomainEvent): void {
    this.events = [entry, ...this.events].slice(0, this.maxItems);
    this.applyFilter();
    setTimeout(() => this.scrollToTop(), 0);
  }

  private scrollToTop(): void {
    const el = this.streamListRef?.nativeElement;
    if (el) el.scrollTop = 0;
  }

  private normalizeEvent(raw: any): DomainEvent {
    return {
      event_id: raw.event_id ?? String(Date.now() + Math.random()),
      event_type: raw.event_type ?? raw.type ?? '',
      topic: raw.topic ?? '',
      occurred_at: raw.occurred_at ?? raw.timestamp ?? new Date().toISOString(),
      actor: raw.actor ?? {
        actor_id: raw.actor_id ?? '',
        actor_name: raw.actor_name ?? 'system',
        persona: raw.persona ?? null,
        actor_type: 'system',
      },
      source: raw.source ?? 'system',
      entity_type: raw.entity_type ?? '',
      entity_id: raw.entity_id ?? '',
      correlation_id: raw.correlation_id ?? null,
      payload: raw.payload ?? {},
      summary: raw.summary ?? '',
    };
  }
}
