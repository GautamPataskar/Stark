import tensorflow as tf
import torch
import numpy as np
from transformers import BertModel, BertTokenizer
from sklearn.ensemble import GradientBoostingClassifier

class HybridThreatModel:
    def __init__(self):
        self.deep_model = self._build_deep_model()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.gradient_boost = GradientBoostingClassifier(n_estimators=200)
        
    def _build_deep_model(self):
        model = tf.keras.Sequential([
            # Convolutional layers for pattern detection
            tf.keras.layers.Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(None, 128)),
            tf.keras.layers.MaxPooling1D(pool_size=2),
            tf.keras.layers.Conv1D(filters=128, kernel_size=3, activation='relu'),
            tf.keras.layers.MaxPooling1D(pool_size=2),
            
            # LSTM layers for sequence analysis
            tf.keras.layers.LSTM(256, return_sequences=True),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.LSTM(128),
            
            # Dense layers for classification
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC()]
        )
        
        return model
    
    def analyze_threat(self, event_data):
        """
        Comprehensive threat analysis using multiple models
        """
        # Deep learning analysis
        sequence_features = self._extract_sequence_features(event_data)
        deep_score = self.deep_model.predict(sequence_features)
        
        # BERT analysis for text
        text_features = self._extract_text_features(event_data['description'])
        
        # Combine features
        combined_features = np.concatenate([
            sequence_features.reshape(1, -1),
            text_features
        ], axis=1)
        
        # Final prediction using gradient boosting
        final_score = self.gradient_boost.predict_proba(combined_features)[0][1]
        
        return {
            'threat_score': float(final_score),
            'deep_learning_score': float(deep_score[0][0]),
            'confidence': self._calculate_confidence(deep_score, final_score),
            'risk_level': self._determine_risk_level(final_score),
            'analysis_details': {
                'sequence_risk': float(sequence_features.mean()),
                'text_risk': float(text_features.mean()),
                'anomaly_score': self._calculate_anomaly_score(combined_features)
            }
        }
    
    def _extract_sequence_features(self, data):
        # Implementation for sequence feature extraction
        return np.array(data['sequence_data']).reshape(1, -1, 128)
    
    def _extract_text_features(self, text):
        encoded = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors='pt'
        )
        
        with torch.no_grad():
            outputs = self.bert(**encoded)
            return outputs.last_hidden_state.mean(dim=1).numpy()
    
    def _calculate_confidence(self, deep_score, final_score):
        return float(np.mean([
            abs(deep_score - 0.5) * 2,
            abs(final_score - 0.5) * 2
        ]))
    
    def _determine_risk_level(self, score):
        if score > 0.9: return 'CRITICAL'
        if score > 0.7: return 'HIGH'
        if score > 0.5: return 'MEDIUM'
        if score > 0.3: return 'LOW'
        return 'MINIMAL'
    
    def _calculate_anomaly_score(self, features):
        # Implementation for anomaly scoring
        return float(np.mean(np.abs(features - np.mean(features))))