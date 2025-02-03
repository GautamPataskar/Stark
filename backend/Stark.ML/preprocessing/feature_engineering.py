import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Dict, Union
import logging

class SecurityFeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feature_names = []
        self.categorical_features = []
        self.numerical_features = []
        
    def fit(self, X: pd.DataFrame, y=None):
        """Fit the feature engineer to the data"""
        try:
            self._identify_features(X)
            return self
        except Exception as e:
            self.logger.error(f"Error in feature engineering fit: {str(e)}")
            raise
            
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform the data with engineered features"""
        try:
            features = []
            
            # Basic features
            basic_features = self._extract_basic_features(X)
            features.append(basic_features)
            
            # Time-based features
            if 'timestamp' in X.columns:
                time_features = self._extract_time_features(X)
                features.append(time_features)
            
            # Behavioral features
            behavioral_features = self._extract_behavioral_features(X)
            features.append(behavioral_features)
            
            # Statistical features
            statistical_features = self._extract_statistical_features(X)
            features.append(statistical_features)
            
            # Combine all features
            combined_features = np.concatenate(features, axis=1)
            
            return combined_features
            
        except Exception as e:
            self.logger.error(f"Error in feature transformation: {str(e)}")
            raise
            
    def _identify_features(self, X: pd.DataFrame):
        """Identify and categorize features"""
        self.numerical_features = list(X.select_dtypes(include=[np.number]).columns)
        self.categorical_features = list(X.select_dtypes(include=['object']).columns)
        
    def _extract_basic_features(self, X: pd.DataFrame) -> np.ndarray:
        """Extract basic features from the data"""
        features = []
        
        # Process numerical features
        for col in self.numerical_features:
            if col in X.columns:
                features.append(X[col].values.reshape(-1, 1))
                
        # Process categorical features
        for col in self.categorical_features:
            if col in X.columns:
                # One-hot encoding for categorical features
                dummies = pd.get_dummies(X[col], prefix=col)
                features.append(dummies.values)
                
        return np.concatenate(features, axis=1) if features else np.array([])
        
    def _extract_time_features(self, X: pd.DataFrame) -> np.ndarray:
        """Extract time-based features"""
        timestamps = pd.to_datetime(X['timestamp'])
        
        time_features = np.column_stack([
            timestamps.dt.hour,
            timestamps.dt.dayofweek,
            timestamps.dt.day,
            timestamps.dt.month,
            timestamps.dt.quarter,
            timestamps.dt.year,
            timestamps.dt.minute / 60.0,  # Normalized minutes
            timestamps.dt.second / 3600.0,  # Normalized seconds
            self._is_business_hours(timestamps),
            self._is_weekend(timestamps)
        ])
        
        return time_features
        
    def _extract_behavioral_features(self, X: pd.DataFrame) -> np.ndarray:
        """Extract behavioral patterns"""
        behavioral_features = []
        
        if 'user_id' in X.columns:
            # User activity patterns
            user_stats = X.groupby('user_id').agg({
                'timestamp': ['count', 'nunique'],
                'event_type': 'nunique',
                'ip_address': 'nunique'
            }).reset_index()
            behavioral_features.append(user_stats.drop('user_id', axis=1).values)
            
        if 'ip_address' in X.columns:
            # Network patterns
            ip_stats = X.groupby('ip_address').agg({
                'timestamp': ['count', 'nunique'],
                'port': ['nunique', 'mean'],
                'protocol': 'nunique'
            }).reset_index()
            behavioral_features.append(ip_stats.drop('ip_address', axis=1).values)
            
        return np.concatenate(behavioral_features, axis=1) if behavioral_features else np.zeros((len(X), 1))
        
    def _extract_statistical_features(self, X: pd.DataFrame) -> np.ndarray:
        """Extract statistical features"""
        statistical_features = []
        
        for col in self.numerical_features:
            if col in X.columns:
                stats = X.groupby('user_id')[col].agg([
                    'mean', 'std', 'min', 'max',
                    lambda x: np.percentile(x, 25),
                    lambda x: np.percentile(x, 75)
                ]).reset_index()
                statistical_features.append(stats.drop('user_id', axis=1).values)
                
        return np.concatenate(statistical_features, axis=1) if statistical_features else np.zeros((len(X), 1))
        
    def _is_business_hours(self, timestamps: pd.Series) -> np.ndarray:
        """Check if timestamp is during business hours (9 AM - 5 PM)"""
        return ((timestamps.dt.hour >= 9) & (timestamps.dt.hour < 17)).astype(int)
        
    def _is_weekend(self, timestamps: pd.Series) -> np.ndarray:
        """Check if timestamp is during weekend"""
        return (timestamps.dt.dayofweek >= 5).astype(int)