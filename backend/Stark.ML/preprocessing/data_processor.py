import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Union, Tuple
import logging

class DataProcessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.logger = logging.getLogger(__name__)
        
    def process_security_data(self, raw_data: Union[Dict, List[Dict]]) -> np.ndarray:
        """
        Comprehensive preprocessing for security event data
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(raw_data) if isinstance(raw_data, dict) else pd.DataFrame(raw_data)
            
            # Process different types of features
            numerical_features = self._process_numerical(df)
            categorical_features = self._process_categorical(df)
            temporal_features = self._process_temporal(df)
            behavioral_features = self._process_behavioral(df)
            
            # Combine all features
            processed_data = np.concatenate([
                numerical_features,
                categorical_features,
                temporal_features,
                behavioral_features
            ], axis=1)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing security data: {str(e)}")
            raise
        
    def _process_numerical(self, df: pd.DataFrame) -> np.ndarray:
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if not numerical_cols.empty:
            if 'numerical' not in self.scalers:
                self.scalers['numerical'] = StandardScaler()
            return self.scalers['numerical'].fit_transform(df[numerical_cols])
        return np.array([])
        
    def _process_categorical(self, df: pd.DataFrame) -> np.ndarray:
        categorical_cols = df.select_dtypes(include=['object']).columns
        encoded_features = []
        
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
            encoded = self.encoders[col].fit_transform(df[col])
            encoded_features.append(encoded.reshape(-1, 1))
            
        return np.concatenate(encoded_features, axis=1) if encoded_features else np.array([])
        
    def _process_temporal(self, df: pd.DataFrame) -> np.ndarray:
        if 'timestamp' not in df.columns:
            return np.zeros((len(df), 1))
            
        timestamps = pd.to_datetime(df['timestamp'])
        temporal_features = np.column_stack([
            timestamps.dt.hour,
            timestamps.dt.dayofweek,
            timestamps.dt.day,
            timestamps.dt.month,
            timestamps.dt.quarter,
            timestamps.dt.year,
            timestamps.dt.minute / 60.0  # Normalized minutes
        ])
        
        if 'temporal' not in self.scalers:
            self.scalers['temporal'] = StandardScaler()
        return self.scalers['temporal'].fit_transform(temporal_features)
        
    def _process_behavioral(self, df: pd.DataFrame) -> np.ndarray:
        """Process behavioral patterns and user activity"""
        behavioral_features = []
        
        if 'user_id' in df.columns:
            user_activity = self._extract_user_patterns(df)
            behavioral_features.append(user_activity)
            
        if 'ip_address' in df.columns:
            network_patterns = self._extract_network_patterns(df)
            behavioral_features.append(network_patterns)
            
        return np.concatenate(behavioral_features, axis=1) if behavioral_features else np.zeros((len(df), 1))
    
    def _extract_user_patterns(self, df: pd.DataFrame) -> np.ndarray:
        """Extract user behavior patterns"""
        user_stats = df.groupby('user_id').agg({
            'timestamp': ['count', 'min', 'max'],
            'event_type': 'nunique'
        }).reset_index()
        
        if 'user_patterns' not in self.scalers:
            self.scalers['user_patterns'] = StandardScaler()
        
        return self.scalers['user_patterns'].fit_transform(user_stats.drop('user_id', axis=1))
    
    def _extract_network_patterns(self, df: pd.DataFrame) -> np.ndarray:
        """Extract network behavior patterns"""
        network_stats = df.groupby('ip_address').agg({
            'timestamp': ['count', 'min', 'max'],
            'port': ['nunique', 'mean']
        }).reset_index()
        
        if 'network_patterns' not in self.scalers:
            self.scalers['network_patterns'] = StandardScaler()
        
        return self.scalers['network_patterns'].fit_transform(network_stats.drop('ip_address', axis=1))