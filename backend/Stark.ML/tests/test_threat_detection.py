import unittest
import numpy as np
from ..models.deep_learning.hybrid_threat_model import HybridThreatModel
from ..models.anomaly_detection.real_time_anomaly_detector import RealTimeAnomalyDetector

class TestThreatDetection(unittest.TestCase):
    def setUp(self):
        self.threat_model = HybridThreatModel()
        self.anomaly_detector = RealTimeAnomalyDetector()
        
    def test_threat_detection(self):
        # Test data
        test_data = {
            'sequence_data': np.random.rand(1, 10, 128),
            'description': 'Suspicious login attempt from unknown IP'
        }
        
        # Get prediction
        result = self.threat_model.analyze_threat(test_data)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('threat_score', result)
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['threat_score'], 0)
        self.assertLessEqual(result['threat_score'], 1)
        
    def test_anomaly_detection(self):
        # Generate test stream
        test_stream = [np.random.rand(128) for _ in range(100)]
        
        # Get anomalies
        results = self.anomaly_detector.detect_anomalies(test_stream)
        
        # Assertions
        self.assertIsInstance(results, list)
        self.assertTrue(all('is_anomaly' in r for r in results))
        self.assertTrue(all('anomaly_score' in r for r in results))