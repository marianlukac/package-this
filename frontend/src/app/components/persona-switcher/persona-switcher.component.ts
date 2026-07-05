import { Component, OnInit, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PersonaService } from '../../services/persona.service';
import { ApiService } from '../../services/api.service';
import { PERSONA_PROFILES } from '../../data/persona-profiles';
import { PersonaProfile } from '../../models/persona-profile';

@Component({
  selector: 'app-persona-switcher',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="relative" role="navigation" aria-label="Persona selector">
      <!-- Compact trigger: initials avatar + name -->
      <button
        (click)="toggleOpen()"
        [attr.aria-expanded]="open"
        aria-haspopup="listbox"
        class="flex items-center gap-2 rounded px-2 py-1 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-dm-gold transition-colors"
        aria-label="Switch active persona"
      >
        @if (currentProfile) {
          <span
            class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold text-white shrink-0"
            [style.background-color]="currentProfile.themeColor"
            aria-hidden="true"
          >{{ currentProfile.initials }}</span>
          <span class="hidden sm:block text-sm font-medium text-white">{{ currentProfile.name }}</span>
        }
        <svg class="w-3 h-3 text-blue-200 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Dropdown panel -->
      @if (open) {
        <div
          role="listbox"
          aria-label="Select persona"
          class="absolute right-0 top-full mt-1 w-72 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-y-auto"
        >
          <div class="p-2">
            <p class="text-xs text-gray-400 font-medium px-2 pb-1 uppercase tracking-wide">Switch Persona</p>
            @for (profile of profiles; track profile.employeeId) {
              <button
                role="option"
                [attr.aria-selected]="profile.employeeId === currentPersonaId"
                (click)="select(profile)"
                (keydown.enter)="select(profile)"
                (keydown.space)="select(profile)"
                class="w-full flex items-center gap-3 px-2 py-2 rounded-md text-left transition-colors hover:bg-gray-50 focus:outline-none focus:bg-blue-50"
                [class.bg-blue-50]="profile.employeeId === currentPersonaId"
                [class.ring-1]="profile.employeeId === currentPersonaId"
                [class.ring-dm-blue]="profile.employeeId === currentPersonaId"
              >
                <span
                  class="flex items-center justify-center w-9 h-9 rounded-full text-sm font-bold text-white shrink-0"
                  [style.background-color]="profile.themeColor"
                  aria-hidden="true"
                >{{ profile.initials }}</span>
                <div class="min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">{{ profile.name }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ profile.role }}</div>
                  <div class="text-xs text-gray-400 truncate mt-0.5">{{ profile.description }}</div>
                </div>
              </button>
            }
          </div>
        </div>
      }
    </div>
  `,
})
export class PersonaSwitcherComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);

  protected profiles: PersonaProfile[] = PERSONA_PROFILES;
  protected open = false;

  get currentPersonaId(): string {
    return this.persona.currentPersonaId();
  }

  get currentProfile(): PersonaProfile | null {
    return this.persona.currentPersonaProfile();
  }

  ngOnInit(): void {
    this.api.getEmployees().subscribe(employees => {
      this.persona.setEmployees(employees);
    });
  }

  toggleOpen(): void {
    this.open = !this.open;
  }

  select(profile: PersonaProfile): void {
    this.persona.setPersona(profile.employeeId);
    this.open = false;
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!(event.target as Element).closest('app-persona-switcher')) {
      this.open = false;
    }
  }
}
