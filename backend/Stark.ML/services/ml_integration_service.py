import numpy as np
import tensorflow as tf
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from ..models.deep_learning.hybrid_threat_model import HybridThreatModel
from ..models.anomaly_detection.real_time_anomaly_detector import RealTimeAnomalyDetector

class MLIntegrationService:
    def __init__(self):
        self.threat_model = HybridThreatModel()
        self.anomaly_detector = RealTimeAnomalyDetector()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.model_metrics = {}
        
    async def analyze_security_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive security event analysis using multiple ML models
        """
        # Run analyses in parallel
        threat_future = self.executor.submit(
            self.threat_model.analyze_threat, 
            event_data
        )
        anomaly_future = self.executor.submit(
            self.anomaly_detector.detect_anomalies,
            [event_data]
        )
        
        # Gather results
        threat_result = threat_future.result()
        anomaly_result = anomaly_future.result()
        
        # Combine analyses
        combined_risk = self._calculate_combined_risk(
            threat_result['threat_score'],
            anomaly_result[0]['anomaly_score']
        )
        
        return {
            'risk_assessment': {
                'combined_risk_score': combined_risk,
                'threat_analysis': threat_result,
                'anomaly_analysis': anomaly_result[0],
                'confidence': self._calculate_confidence(threat_result, anomaly_result[0])
            },
            'recommendations': self._generate_recommendations(combined_risk),
            'model_metrics': self.get_model_metrics()
        }
    
    def _calculate_combined_risk(self, threat_score: float, anomaly_score: float) -> float:
        """
        Calculate combined risk score using weighted average
        """
        weights = {
            'threat': 0.6,
            'anomaly': 0.4
        }
        return (threat_score * weights['threat'] + 
                anomaly_score * weights['anomaly'])
    
    def _calculate_confidence(self, threat_result: Dict, anomaly_result: Dict) -> float:
        """
        Calculate overall confidence score
        """
        threat_confidence = threat_result.get('confidence', 0.5)
        anomaly_confidence = anomaly_result.get('confidence', 0.5)
        
        return np.mean([threat_confidence, anomaly_confidence])
    
    def _generate_recommendations(self, risk_score: float) -> List[str]:
        """
        Generate security recommendations based on risk score
        """
        recommendations = []
        
        if risk_score > 0.8:
            recommendations.extend([
                "Immediate investigation required",
                "Consider system isolation",
                "Activate incident response team"
            ])
        elif risk_score > 0.6:
            recommendations.extend([
                "Increase monitoring",
                "Review recent system changes",
                "Prepare incident response team"
            ])
        elif risk_score > 0.4:
            recommendations.extend([
                "Monitor situation",
                "Review security logs",
                "Update threat signatures"
            ])
            
        return recommendations
    
    def get_model_metrics(self) -> Dict[str, Any]:
        """
        Get current model performance metrics
        """
        return {
            'threat_model': {
                'accuracy': self.model_metrics.get('threat_accuracy', 0.0),
                'precision': self.model_metrics.get('threat_precision', 0.0),
                'recall': self.model_metrics.get('threat_recall', 0.0),
                'f1_score': self.model_metrics.get('threat_f1', 0.0)
            },
            'anomaly_detector': {
                'accuracy': self.model_metrics.get('anomaly_accuracy', 0.0),
                'false_positive_rate': self.model_metrics.get('false_positive_rate', 0.0),
                'detection_rate': self.model_metrics.get('detection_rate', 0.0)
            }
        }
    
    async def retrain_models(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrain models with new data
        """
        try:
            # Retrain threat model
            threat_metrics = await self._retrain_threat_model(new_data)
            
            # Retrain anomaly detector
            anomaly_metrics = await self._retrain_anomaly_detector(new_data)
            
            # Update metrics
            self.model_metrics.update(threat_metrics)
            self.model_metrics.update(anomaly_metrics)
            
            return {
                'status': 'success',
                'threat_model_improvement': threat_metrics['improvement'],
                'anomaly_detector_improvement': anomaly_metrics['improvement']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }