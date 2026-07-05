import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { MapLocation, LocationType } from '../models/map.model';
import { Truck, TruckRoute } from '../models/truck.model';

export const SCRANTON_CENTER = { lat: 41.4090, lng: -75.6624 };

const LOCATION_CONFIG: Record<string, { emoji: string; color: string; size: number }> = {
  warehouse: { emoji: '🏢', color: '#FF6B00', size: 42 },
  customer:  { emoji: '📦', color: '#3b82f6', size: 34 },
  food:      { emoji: '🍔', color: '#ef4444', size: 34 },
  donut:     { emoji: '🍩', color: '#a855f7', size: 34 },
};

@Injectable({ providedIn: 'root' })
export class MapService {
  private _map: any = null;
  private _datasource: any = null;
  private _polylineLayer: any = null;
  private _atlas: any = null;
  private _locationMarkers: any[] = [];
  private _truckMarkers: Map<string, any> = new Map();
  private _routeLines: Map<string, any> = new Map();
  private _clickCallback: ((props: any) => void) | null = null;

  get isLoaded(): boolean {
    return this._map !== null;
  }

  async initMap(containerId: string): Promise<void> {
    try {
      const atlasModule = await import('azure-maps-control');
      const atlas = (atlasModule as any).default ?? atlasModule;
      this._atlas = atlas;

      const subscriptionKey = environment.azureMapsKey ?? '';
      const mapOptions: any = {
        center: [SCRANTON_CENTER.lng, SCRANTON_CENTER.lat],
        zoom: 13,
        style: 'road',
        language: 'en-US',
      };

      if (subscriptionKey) {
        mapOptions.authOptions = { authType: 'subscriptionKey', subscriptionKey };
      }

      this._map = new atlas.Map(containerId, mapOptions);

      await new Promise<void>((resolve) => {
        this._map.events.add('ready', () => {
          // Datasource + layer only needed for route polylines
          this._datasource = new atlas.source.DataSource();
          this._map.sources.add(this._datasource);
          this._polylineLayer = new atlas.layer.LineLayer(this._datasource, undefined, {
            strokeColor: ['get', 'color'],
            strokeWidth: 3,
          });
          this._map.layers.add(this._polylineLayer);
          resolve();
        });
        this._map.events.add('error', () => resolve());
      });
    } catch {
      // Azure Maps SDK not available — silently skip
    }
  }

  addLocationMarkers(locations: MapLocation[]): void {
    if (!this._atlas || !this._map) return;

    // Clear previous location markers
    for (const m of this._locationMarkers) {
      this._map.markers.remove(m);
    }
    this._locationMarkers = [];

    for (const loc of locations) {
      const cfg = LOCATION_CONFIG[loc.location_type as LocationType]
        ?? LOCATION_CONFIG['customer'];
      const marker = new this._atlas.HtmlMarker({
        htmlContent: this._circlePin(cfg.emoji, cfg.color, cfg.size),
        position: [loc.lng, loc.lat],
        anchor: 'center',
      });
      this._map.markers.add(marker);
      this._locationMarkers.push(marker);
    }
  }

  addOrUpdateTruckMarker(truck: Truck): void {
    if (!this._atlas || !this._map) return;
    if (!Number.isFinite(truck.current_lat) || !Number.isFinite(truck.current_lng)) return;

    const color = truck.delay_reason  ? '#ef4444'
                : truck.status === 'in_transit' ? '#f59e0b'
                : '#6b7280';
    const html = this._circlePin('🚛', color, 42);

    const existing = this._truckMarkers.get(truck.truck_id);
    if (existing) {
      existing.setOptions({
        htmlContent: html,
        position: [truck.current_lng, truck.current_lat],
      });
    } else {
      const marker = new this._atlas.HtmlMarker({
        htmlContent: html,
        position: [truck.current_lng, truck.current_lat],
        anchor: 'center',
      });
      this._map.events.add('click', marker, () => {
        this._clickCallback?.({ truckId: truck.truck_id, status: truck.status });
      });
      this._map.markers.add(marker);
      this._truckMarkers.set(truck.truck_id, marker);
    }
  }

  private _circlePin(emoji: string, color: string, size: number): string {
    const fontSize = Math.round(size * 0.48);
    return `<div style="
      width:${size}px;height:${size}px;
      background:${color};
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      border:3px solid white;
      box-shadow:0 2px 8px rgba(0,0,0,0.45);
      cursor:pointer;
      font-size:${fontSize}px;
      line-height:1;
      user-select:none;
    ">${emoji}</div>`;
  }

  addOrUpdateRoutePolyline(truckId: string, route: TruckRoute): void {
    if (!this._atlas || !this._datasource || !route.geometry?.length) return;

    const atlas = this._atlas;
    const coordinates = route.geometry.map(([lat, lng]) => [lng, lat] as [number, number]);
    const line = new atlas.data.Feature(
      new atlas.data.LineString(coordinates),
      { color: '#FF6B00', truckId }
    );

    const existing = this._routeLines.get(truckId);
    if (existing) this._datasource.remove(existing);
    this._datasource.add(line);
    this._routeLines.set(truckId, line);
  }

  removeRoutePolyline(truckId: string): void {
    const existing = this._routeLines.get(truckId);
    if (existing && this._datasource) {
      this._datasource.remove(existing);
      this._routeLines.delete(truckId);
    }
  }

  onMarkerClick(callback: (properties: any) => void): void {
    this._clickCallback = callback;
  }

  panTo(lat: number, lng: number): void {
    if (this._map) {
      this._map.setCamera({ center: [lng, lat], duration: 500 });
    }
  }

  destroyMap(): void {
    if (this._map) {
      for (const m of this._locationMarkers) this._map.markers.remove(m);
      this._truckMarkers.forEach(m => this._map.markers.remove(m));
      this._map.dispose();
      this._map = null;
      this._datasource = null;
      this._polylineLayer = null;
      this._locationMarkers = [];
      this._truckMarkers.clear();
      this._routeLines.clear();
      this._clickCallback = null;
    }
  }
}
