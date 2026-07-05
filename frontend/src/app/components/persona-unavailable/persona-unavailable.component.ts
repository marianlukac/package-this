import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PersonaService } from '../../services/persona.service';

@Component({
  selector: 'app-persona-unavailable',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="inline-flex items-center gap-2" [attr.aria-label]="ariaLabel">
      <button
        disabled
        class="px-3 py-1.5 text-xs font-medium rounded border border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed"
        [attr.title]="tooltip"
        [attr.aria-disabled]="true"
      >
        {{ action }}
      </button>
      <span class="text-xs text-gray-400 italic">{{ tooltip }}</span>
    </div>
  `,
})
export class PersonaUnavailableComponent {
  @Input({ required: true }) requiredRole!: string;
  @Input({ required: true }) action!: string;

  private persona = inject(PersonaService);

  get tooltip(): string {
    const profile = this.persona.currentPersonaProfile();
    const currentName = profile?.name ?? this.persona.currentPersonaId();
    return `This action requires ${this.requiredRole}. You are currently ${currentName}.`;
  }

  get ariaLabel(): string {
    return `${this.action} — unavailable. ${this.tooltip}`;
  }
}
