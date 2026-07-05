import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PersonaService } from './services/persona.service';
import { ApiService } from './services/api.service';
import { RealtimeService } from './services/realtime.service';
import { PersonaSwitcherComponent } from './components/persona-switcher/persona-switcher.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule, PersonaSwitcherComponent],
  template: `
    <div class="min-h-screen flex flex-col">
      <!-- Top nav -->
      <header class="bg-dm-blue text-white shadow-md" role="banner">
        <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div class="flex items-center gap-4">
            <a routerLink="/dashboard" class="font-bold text-base tracking-tight hover:text-dm-gold transition-colors shrink-0">
              📦 DM Package Manager
            </a>
            <nav class="hidden lg:flex gap-3 text-sm" aria-label="Main navigation">
              <a routerLink="/dashboard" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Dashboard</a>
              <a routerLink="/packages" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Packages</a>
              <a routerLink="/complaints" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Complaints</a>
              <a routerLink="/customers" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Customers</a>
              <a routerLink="/sales" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Sales</a>
              <a routerLink="/map" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Trucks</a>
              <a routerLink="/events" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                 class="pb-1 hover:text-dm-gold transition-colors">Events</a>
              @if (persona.isManager()) {
                <a routerLink="/demo" routerLinkActive="text-dm-gold border-b-2 border-dm-gold"
                   class="pb-1 hover:text-dm-gold transition-colors text-dm-gold">Demo Controls</a>
              }
            </nav>
          </div>
          <app-persona-switcher />
        </div>
      </header>

      <!-- Main content -->
      <main class="flex-1 max-w-7xl mx-auto w-full px-4 py-6" id="main-content" tabindex="-1">
        <router-outlet />
      </main>

      <!-- Footer -->
      <footer class="bg-white border-t border-gray-200 text-xs text-gray-400 text-center py-2" role="contentinfo">
        Dunder Mifflin Package Manager &mdash; Agentic AI Workshop Baseline
      </footer>
    </div>
  `,
})
export class AppComponent implements OnInit {
  protected persona = inject(PersonaService);
  private api = inject(ApiService);
  private realtime = inject(RealtimeService);

  ngOnInit(): void {
    this.api.getEmployees().subscribe(employees => this.persona.setEmployees(employees));
    this.realtime.connect();
  }
}
