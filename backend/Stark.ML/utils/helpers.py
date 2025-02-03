import numpy as np
from typing import Dict, List, Union, Any
import json
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

def calculate_threat_score(predictions: np.ndarray, weights: np.ndarray = None) -> float:
    """Calculate weighted threat score from multiple predictions"""
    if weights is None:
        weights = np.ones(len(predictions)) / len(predictions)
    return float(np.average(predictions, weights=weights))

def validate_input_data(data: Dict[str, Any]) -> bool:
    """Validate input data structure and types"""
    required_fields = ['timestamp', 'source_ip', 'event_type']
    try:
        # Check required fields
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
                
        # Validate timestamp
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            logger.error("Invalid timestamp format")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating input data: {str(e)}")
        return False

def generate_event_id(event_data: Dict[str, Any]) -> str:
    """Generate unique event ID based on event data"""
    event_string = json.dumps(event_data, sort_keys=True)
    return hashlib.sha256(event_string.encode()).hexdigest()

def format_prediction_output(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Format prediction output for API response"""
    try:
        return {
            'prediction_id': generate_event_id(predictions),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'threat_score': float(predictions.get('threat_score', 0)),
            'confidence': float(predictions.get('confidence', 0)),
            'risk_level': predictions.get('risk_level', 'UNKNOWN'),
            'details': predictions.get('details', {}),
            'recommendations': generate_recommendations(predictions)
        }
    except Exception as e:
        logger.error(f"Error formatting prediction output: {str(e)}")
        raise

def generate_recommendations(predictions: Dict[str, Any]) -> List[str]:
    """Generate security recommendations based on predictions"""
    threat_score = predictions.get('threat_score', 0)
    recommendations = []
    
    if threat_score > 0.8:
        recommendations.extend([
            "CRITICAL: Immediate action required",
            "Isolate affected systems",
            "Initiate incident response protocol",
            "Notify security team immediately"
        ])
    elif threat_score > 0.6:
        recommendations.extend([
            "HIGH: Urgent attention needed",
            "Investigate suspicious activity",
            "Increase monitoring",
            "Prepare for potential incident response"
        ])
    elif threat_score > 0.4:
        recommendations.extend([
            "MEDIUM: Enhanced monitoring required",
            "Review security logs",
            "Update security rules if needed"
        ])
    else:
        recommendations.extend([
            "LOW: Continue normal monitoring",
            "Log for future reference"
        ])
    
    return recommendations

def parse_log_entry(log_entry: str) -> Dict[str, Any]:
    """Parse log entry into structured data"""
    try:
        return json.loads(log_entry)
    except json.JSONDecodeError:
        logger.error("Invalid log entry format")
        return {}

def calculate_metrics(true_labels: np.ndarray, predictions: np.ndarray) -> Dict[str, float]:
    """Calculate various performance metrics"""
    try:
        tp = np.sum((true_labels == 1) & (predictions == 1))
        fp = np.sum((true_labels == 0) & (predictions == 1))
        tn = np.sum((true_labels == 0) & (predictions == 0))
        fn = np.sum((true_labels == 1) & (predictions == 0))
        
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise