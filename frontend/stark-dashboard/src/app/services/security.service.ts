import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { webSocket } from 'rxjs/webSocket';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SecurityService {
  private apiUrl = environment.apiUrl;
  private wsUrl = environment.wsUrl;
  private socket: any;

  private threatLevelSubject = new BehaviorSubject<number>(0);
  public threatLevel$ = this.threatLevelSubject.asObservable();

  constructor(private http: HttpClient) {
    this.initializeWebSocket();
  }

  private initializeWebSocket() {
    this.socket = webSocket(this.wsUrl);
    this.socket.subscribe(
      (message: any) => this.handleWebSocketMessage(message),
      (error: any) => console.error('WebSocket error:', error),
      () => console.log('WebSocket connection closed')
    );
  }

  private handleWebSocketMessage(message: any) {
    switch (message.type) {
      case 'THREAT_UPDATE':
        this.threatLevelSubject.next(message.data.threatLevel);
        break;
      case 'ANOMALY_DETECTED':
        // Handle anomaly detection
        break;
      case 'MODEL_METRICS':
        // Handle ML model metrics update
        break;
    }
  }

  getAnomalies(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/security/anomalies`);
  }

  getMLMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/security/ml-metrics`);
  }

  getRealTimeThreats(): Observable<any> {
    return this.socket.multiplex(
      () => ({ subscribe: 'threats' }),
      () => ({ unsubscribe: 'threats' }),
      message => message.type === 'THREAT_UPDATE'
    );
  }

  analyzeThreat(data: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/security/analyze`, data);
  }

  getDashboardMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/security/dashboard-metrics`);
  }

  reportIncident(incident: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/security/incidents`, incident);
  }
}