import { Component, Input, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { PackageHistoryEntry } from '../../models/package.model';

const EVENT_ICONS: Record<string, string> = {
  package_created: '📦',
  line_item_added: '➕',
  line_item_changed: '✏️',
  status_changed: '🔄',
  location_updated: '📍',
  assigned_to_truck: '🚚',
  truck_rerouted: '🗺️',
  delivered: '✅',
  returned: '↩️',
  damaged: '💥',
  cancelled: '❌',
  complaint_created: '🚨',
  complaint_updated: '📝',
  manager_action_performed: '⚡',
  delay_recorded: '⏳',
};

@Component({
  selector: 'app-package-history',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card">
      <h2 class="font-semibold text-gray-800 mb-3">Package History</h2>
      @if (loading) {
        <p class="text-xs text-gray-400">Loading history…</p>
      } @else if (entries.length === 0) {
        <p class="text-xs text-gray-400">No history entries yet.</p>
      } @else {
        <ol class="relative border-l border-gray-200 space-y-3" aria-label="Package history timeline">
          @for (entry of entries; track entry.id) {
            <li class="ml-4">
              <span class="absolute -left-1.5 flex h-3 w-3 items-center justify-center rounded-full bg-white border border-gray-300"
                    aria-hidden="true">
              </span>
              <div class="text-xs">
                <div class="flex items-start gap-1">
                  <span aria-hidden="true">{{ icon(entry.event_type) }}</span>
                  <span class="font-medium text-gray-800 capitalize">{{ formatEventType(entry.event_type) }}</span>
                </div>
                <div class="text-gray-400">
                  {{ entry.actor_name ?? entry.actor_id ?? 'system' }}
                  · {{ entry.timestamp | date:'short' }}
                  @if (entry.source) { · <span class="italic">{{ entry.source }}</span> }
                </div>
                @if (diffEvents.includes(entry.event_type) && entry.previous_value && entry.new_value) {
                  <div class="text-gray-500 mt-0.5 font-mono text-xs">
                    {{ formatDiff(entry.previous_value) }} → {{ formatDiff(entry.new_value) }}
                  </div>
                }
                @if (entry.event_type === 'manager_action_performed' && entry.new_value) {
                  <div class="text-indigo-600 font-semibold mt-0.5">{{ formatDiff(entry.new_value) }}</div>
                }
                @if (entry.reason) {
                  <div class="text-gray-500 mt-0.5">{{ entry.reason }}</div>
                }
              </div>
            </li>
          }
        </ol>
      }
    </div>
  `,
})
export class PackageHistoryComponent implements OnInit {
  @Input({ required: true }) packageId!: string;
  private api = inject(ApiService);
  protected entries: PackageHistoryEntry[] = [];
  protected loading = true;

  protected readonly diffEvents = ['status_changed', 'priority_changed', 'location_updated'];

  ngOnInit(): void {
    this.api.getPackageHistory(this.packageId).subscribe({
      next: (res) => { this.entries = res.history; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  icon(eventType: string): string {
    return EVENT_ICONS[eventType] ?? '•';
  }

  formatEventType(eventType: string): string {
    return eventType.split('_').join(' ');
  }

  formatDiff(jsonStr: string | null): string {
    if (!jsonStr) return '—';
    try {
      const parsed = JSON.parse(jsonStr);
      if (typeof parsed === 'object' && parsed !== null) {
        const values = Object.values(parsed);
        return values.length === 1 ? String(values[0]) : JSON.stringify(parsed);
      }
      return String(parsed);
    } catch {
      return jsonStr;
    }
  }
}
