import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
  },
  {
    path: 'packages',
    loadComponent: () =>
      import('./components/package-list/package-list.component').then(m => m.PackageListComponent),
  },
  {
    path: 'packages/:id',
    loadComponent: () =>
      import('./components/package-detail/package-detail.component').then(m => m.PackageDetailComponent),
  },
  {
    path: 'sales/new',
    loadComponent: () =>
      import('./components/sale-create/sale-create.component').then(m => m.SaleCreateComponent),
  },
  {
    path: 'complaints',
    loadComponent: () =>
      import('./components/complaint-list/complaint-list.component').then(m => m.ComplaintListComponent),
  },
  {
    path: 'complaints/:id',
    loadComponent: () =>
      import('./components/complaint-detail/complaint-detail.component').then(m => m.ComplaintDetailComponent),
  },
  {
    path: 'map',
    loadComponent: () =>
      import('./components/map-view/map-view.component').then(m => m.MapViewComponent),
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
