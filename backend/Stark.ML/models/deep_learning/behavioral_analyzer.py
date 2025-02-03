import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from sklearn.preprocessing import StandardScaler

class BehavioralAnalyzer:
    def __init__(self):
        self.sequence_model = self._build_sequence_model()
        self.pattern_detector = self._build_pattern_detector()
        self.scaler = StandardScaler()
        
    def _build_sequence_model(self):
        model = tf.keras.Sequential([
            Bidirectional(LSTM(256, return_sequences=True, input_shape=(None, 128))),
            Dropout(0.4),
            Bidirectional(LSTM(128, return_sequences=True)),
            Dropout(0.3),
            Bidirectional(LSTM(64)),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-4),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_pattern_detector(self):
        return tf.keras.Sequential([
            Dense(128, activation='relu', input_shape=(128,)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(16, activation='softmax')
        ])

    def analyze_behavior(self, user_data, historical_patterns):
        """
        Analyzes user behavior patterns for anomalies
        """
        # Normalize data
        normalized_data = self.scaler.fit_transform(user_data)
        
        # Sequence analysis
        sequence_score = self.sequence_model.predict(normalized_data)
        
        # Pattern analysis
        pattern_analysis = self.pattern_detector.predict(normalized_data)
        
        # Compare with historical patterns
        deviation_score = self._calculate_pattern_deviation(
            pattern_analysis, 
            historical_patterns
        )
        
        return {
            'risk_score': float(sequence_score.mean()),
            'pattern_deviation': float(deviation_score),
            'anomaly_detected': bool(sequence_score.mean() > 0.7),
            'behavior_patterns': pattern_analysis.tolist(),
            'analysis_details': {
                'sequence_confidence': float(abs(sequence_score.mean() - 0.5) * 2),
                'pattern_confidence': float(1 - deviation_score),
                'risk_factors': self._identify_risk_factors(pattern_analysis)
            }
        }
    
    def _calculate_pattern_deviation(self, current, historical):
        return np.mean(np.abs(current - historical))
    
    def _identify_risk_factors(self, patterns):
        # Analyze patterns for specific risk factors
        risk_factors = []
        pattern_means = np.mean(patterns, axis=0)
        
        if pattern_means[0] > 0.8:
            risk_factors.append('Unusual Access Pattern')
        if pattern_means[1] > 0.7:
            risk_factors.append('Temporal Anomaly')
        if pattern_means[2] > 0.6:
            risk_factors.append('Resource Usage Deviation')
            
        return risk_factors