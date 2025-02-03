import { Component, OnInit } from '@angular/core';
import { SecurityService } from '../services/security.service';
import { Chart } from 'chart.js';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-security-dashboard',
  template: `
    <div class="dashboard-container">
      <div class="threat-metrics">
        <mat-card>
          <mat-card-title>Real-Time Threat Analysis</mat-card-title>
          <canvas #threatChart></canvas>
        </mat-card>
      </div>
      
      <div class="anomaly-detection">
        <mat-card>
          <mat-card-title>Anomaly Detection</mat-card-title>
          <div class="anomaly-grid">
            <div *ngFor="let anomaly of anomalies$ | async">
              <mat-card class="anomaly-card" [class.high-risk]="anomaly.riskScore > 0.7">
                <h3>{{ anomaly.type }}</h3>
                <p>Risk Score: {{ anomaly.riskScore | number:'1.2-2' }}</p>
                <p>Detected: {{ anomaly.timestamp | date:'short' }}</p>
              </mat-card>
            </div>
          </div>
        </mat-card>
      </div>

      <div class="ml-metrics">
        <mat-card>
          <mat-card-title>ML Model Performance</mat-card-title>
          <div class="metrics-grid">
            <div class="metric">
              <h4>Accuracy</h4>
              <div class="metric-value">{{ (mlMetrics$ | async)?.accuracy | percent }}</div>
            </div>
            <div class="metric">
              <h4>Precision</h4>
              <div class="metric-value">{{ (mlMetrics$ | async)?.precision | percent }}</div>
            </div>
            <div class="metric">
              <h4>Recall</h4>
              <div class="metric-value">{{ (mlMetrics$ | async)?.recall | percent }}</div>
            </div>
          </div>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      padding: 20px;
    }

    .anomaly-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
    }

    .anomaly-card {
      padding: 15px;
      transition: transform 0.2s;
    }

    .anomaly-card:hover {
      transform: translateY(-5px);
    }

    .high-risk {
      border-left: 4px solid #ff4444;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
    }

    .metric-value {
      font-size: 24px;
      font-weight: bold;
      color: #2196F3;
    }
  `]
})
export class SecurityDashboardComponent implements OnInit {
  anomalies$: Observable<any[]>;
  mlMetrics$: Observable<any>;
  private chart: any;

  constructor(private securityService: SecurityService) {
    this.anomalies$ = this.securityService.getAnomalies();
    this.mlMetrics$ = this.securityService.getMLMetrics();
  }

  ngOnInit() {
    this.initializeChart();
    this.startRealTimeUpdates();
  }

  private initializeChart() {
    const ctx = document.getElementById('threatChart');
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Threat Level',
          data: [],
          borderColor: '#2196F3',
          fill: false
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            max: 1
          }
        }
      }
    });
  }

  private startRealTimeUpdates() {
    this.securityService.getRealTimeThreats().subscribe(threat => {
      this.updateChart(threat);
    });
  }

  private updateChart(threat: any) {
    const timestamp = new Date().toLocaleTimeString();
    
    this.chart.data.labels.push(timestamp);
    this.chart.data.datasets[0].data.push(threat.score);

    if (this.chart.data.labels.length > 20) {
      this.chart.data.labels.shift();
      this.chart.data.datasets[0].data.shift();
    }

    this.chart.update();
  }
}