import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.models import Sequential
from typing import Dict, Any, List

class NeuralThreatDetector:
    def __init__(self):
        self.model = self._build_model()
        self.threshold = 0.85
        self.feature_dim = 128
        
    def _build_model(self) -> Sequential:
        model = Sequential([
            # Input layer with advanced LSTM
            Bidirectional(LSTM(256, return_sequences=True, input_shape=(None, self.feature_dim))),
            Dropout(0.4),
            
            # Deep LSTM layers
            Bidirectional(LSTM(128, return_sequences=True)),
            Dropout(0.3),
            Bidirectional(LSTM(64)),
            
            # Dense layers for feature extraction
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC()]
        )
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, epochs: int = 50, batch_size: int = 32) -> Dict:
        """Train the neural threat detector"""
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(patience=5),
                tf.keras.callbacks.ModelCheckpoint(
                    'best_model.h5',
                    save_best_only=True
                )
            ]
        )
        
        return {
            'training_accuracy': history.history['accuracy'][-1],
            'validation_accuracy': history.history['val_accuracy'][-1],
            'training_loss': history.history['loss'][-1],
            'validation_loss': history.history['val_loss'][-1]
        }
    
    def predict_threat(self, data: np.ndarray) -> Dict[str, Any]:
        """Predict threats from input data"""
        predictions = self.model.predict(data)
        threat_scores = predictions.flatten()
        
        # Calculate confidence scores
        confidence_scores = np.abs(threat_scores - 0.5) * 2
        
        # Generate detailed analysis
        analysis = self._generate_analysis(threat_scores, confidence_scores)
        
        return {
            'threat_scores': threat_scores.tolist(),
            'is_threat': (threat_scores > self.threshold).tolist(),
            'confidence': confidence_scores.tolist(),
            'analysis': analysis
        }
    
    def _generate_analysis(self, threat_scores: np.ndarray, confidence_scores: np.ndarray) -> List[Dict]:
        """Generate detailed analysis for each prediction"""
        analysis = []
        
        for threat_score, confidence in zip(threat_scores, confidence_scores):
            analysis.append({
                'risk_level': self._get_risk_level(threat_score),
                'confidence_level': self._get_confidence_level(confidence),
                'requires_attention': threat_score > self.threshold,
                'score_details': {
                    'raw_score': float(threat_score),
                    'confidence': float(confidence),
                    'normalized_risk': float(threat_score * confidence)
                }
            })
        
        return analysis
    
    def _get_risk_level(self, score: float) -> str:
        if score > 0.8: return 'CRITICAL'
        if score > 0.6: return 'HIGH'
        if score > 0.4: return 'MEDIUM'
        return 'LOW'
    
    def _get_confidence_level(self, confidence: float) -> str:
        if confidence > 0.8: return 'HIGH'
        if confidence > 0.5: return 'MEDIUM'
        return 'LOW'