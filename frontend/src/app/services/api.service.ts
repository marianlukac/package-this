import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { PersonaService } from './persona.service';
import {
  Package, PackageListResponse, PackageHistoryResponse, LineItem,
} from '../models/package.model';
import { Complaint } from '../models/complaint.model';
import { Truck, TruckDetail, TruckLocation, TruckRoute, AssignPackageRequest, RerouteRequest } from '../models/truck.model';
import { MapLocation } from '../models/map.model';
import { Employee } from '../models/employee.model';
import { OperationalSummary } from '../models/sale.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private persona = inject(PersonaService);
  private base = environment.apiBaseUrl;

  private headers(): Record<string, string> {
    const id = this.persona.currentPersonaId();
    return id ? { 'X-Persona-Id': id } : {};
  }

  // --- Employees ---
  getEmployees(): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.base}/employees`, { headers: this.headers() });
  }

  // --- Packages ---
  getPackages(params?: Record<string, string | number>): Observable<PackageListResponse> {
    let p = new HttpParams();
    if (params) Object.entries(params).forEach(([k, v]) => p = p.set(k, String(v)));
    return this.http.get<PackageListResponse>(`${this.base}/packages`, { headers: this.headers(), params: p });
  }

  getPackage(id: string): Observable<Package> {
    return this.http.get<Package>(`${this.base}/packages/${id}`, { headers: this.headers() });
  }

  createPackage(body: object): Observable<Package> {
    return this.http.post<Package>(`${this.base}/packages`, body, { headers: this.headers() });
  }

  updatePackage(id: string, body: object): Observable<Package> {
    return this.http.patch<Package>(`${this.base}/packages/${id}`, body, { headers: this.headers() });
  }

  deletePackage(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/packages/${id}`, { headers: this.headers() });
  }

  getPackageHistory(id: string): Observable<PackageHistoryResponse> {
    return this.http.get<PackageHistoryResponse>(`${this.base}/packages/${id}/history`, { headers: this.headers() });
  }

  advanceStatus(id: string, status: string, reason?: string): Observable<Package> {
    return this.http.post<Package>(`${this.base}/packages/${id}/status`, { status, reason }, { headers: this.headers() });
  }

  recordDelay(id: string, delay_reason: string, delay_duration_hours: number): Observable<Package> {
    return this.http.post<Package>(`${this.base}/packages/${id}/delay`, { delay_reason, delay_duration_hours }, { headers: this.headers() });
  }

  addLineItem(packageId: string, body: object): Observable<LineItem> {
    return this.http.post<LineItem>(`${this.base}/packages/${packageId}/line-items`, body, { headers: this.headers() });
  }

  updateLineItem(packageId: string, itemId: number, body: object): Observable<LineItem> {
    return this.http.patch<LineItem>(`${this.base}/packages/${packageId}/line-items/${itemId}`, body, { headers: this.headers() });
  }

  removeLineItem(packageId: string, itemId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/packages/${packageId}/line-items/${itemId}`, { headers: this.headers() });
  }

  getAtRiskPackages(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/packages/at-risk`, { headers: this.headers() });
  }

  getDelayedPackages(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/packages/delayed`, { headers: this.headers() });
  }

  // --- Sales ---
  createSale(body: object): Observable<any> {
    return this.http.post<any>(`${this.base}/sales`, body, { headers: this.headers() });
  }

  getSales(): Observable<any> {
    return this.http.get<any>(`${this.base}/sales`, { headers: this.headers() });
  }

  getSale(id: string): Observable<any> {
    return this.http.get<any>(`${this.base}/sales/${id}`, { headers: this.headers() });
  }

  // --- Complaints ---
  getComplaints(params?: Record<string, string>): Observable<Complaint[]> {
    let p = new HttpParams();
    if (params) Object.entries(params).forEach(([k, v]) => p = p.set(k, v));
    return this.http.get<Complaint[]>(`${this.base}/complaints`, { headers: this.headers(), params: p });
  }

  getComplaint(id: string): Observable<Complaint> {
    return this.http.get<Complaint>(`${this.base}/complaints/${id}`, { headers: this.headers() });
  }

  createComplaint(body: object): Observable<Complaint> {
    return this.http.post<Complaint>(`${this.base}/complaints`, body, { headers: this.headers() });
  }

  updateComplaint(id: string, description: string): Observable<Complaint> {
    return this.http.patch<Complaint>(`${this.base}/complaints/${id}`, { description }, { headers: this.headers() });
  }

  closeComplaint(id: string): Observable<Complaint> {
    return this.http.post<Complaint>(`${this.base}/complaints/${id}/close`, {}, { headers: this.headers() });
  }

  // --- Manager actions ---
  performManagerAction(action: string, entity_id: string, reason: string, payload: object = {}): Observable<any> {
    return this.http.post<any>(`${this.base}/manager-actions`, {
      action, entity_id, reason, payload, source: 'ui',
    }, { headers: this.headers() });
  }

  // --- Trucks ---
  getTrucks(): Observable<Truck[]> {
    return this.http.get<Truck[]>(`${this.base}/trucks`, { headers: this.headers() });
  }

  getTruck(truckId: string): Observable<TruckDetail> {
    return this.http.get<TruckDetail>(`${this.base}/trucks/${truckId}`, { headers: this.headers() });
  }

  getTruckLocation(truckId: string): Observable<TruckLocation> {
    return this.http.get<TruckLocation>(`${this.base}/trucks/${truckId}/current-location`, { headers: this.headers() });
  }

  getTruckRoute(truckId: string): Observable<TruckRoute> {
    return this.http.get<TruckRoute>(`${this.base}/trucks/${truckId}/current-route`, { headers: this.headers() });
  }

  assignPackage(truckId: string, body: AssignPackageRequest): Observable<any> {
    return this.http.post<any>(`${this.base}/trucks/${truckId}/assign`, body, { headers: this.headers() });
  }

  dispatchTruck(truckId: string): Observable<any> {
    return this.http.post<any>(`${this.base}/trucks/${truckId}/dispatch`, {}, { headers: this.headers() });
  }

  rerouteTruck(truckId: string, body: RerouteRequest): Observable<any> {
    return this.http.post<any>(`${this.base}/trucks/${truckId}/reroute`, body, { headers: this.headers() });
  }

  getActiveDeliveries(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/deliveries/active`, { headers: this.headers() });
  }

  // --- Map ---
  getMapLocations(): Observable<MapLocation[]> {
    return this.http.get<MapLocation[]>(`${this.base}/map/markers`, { headers: this.headers() });
  }

  // --- Events ---
  getEvents(limit = 50, filters?: {
    topic?: string;
    event_type?: string;
    entity_type?: string;
    entity_id?: string;
    actor_id?: string;
    source?: string;
    correlation_id?: string;
    since?: string;
  }): Observable<any[]> {
    let p = new HttpParams().set('limit', String(limit));
    if (filters) {
      Object.entries(filters).forEach(([k, v]) => { if (v) p = p.set(k, v); });
    }
    return this.http.get<any[]>(`${this.base}/events`, { headers: this.headers(), params: p });
  }

  // --- Operational summary ---
  getOperationalSummary(): Observable<OperationalSummary> {
    return this.http.get<OperationalSummary>(`${this.base}/operational-summary`, { headers: this.headers() });
  }

  // --- Customers ---
  getCustomers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/customers`, { headers: this.headers() });
  }

  // --- Demo ---
  resetDemo(): Observable<any> {
    return this.http.post<any>(`${this.base}/demo/reset`, {}, { headers: this.headers() });
  }

  runScenario(name: string): Observable<any> {
    return this.http.post<any>(`${this.base}/demo/scenarios/${name}`, {}, { headers: this.headers() });
  }
}
