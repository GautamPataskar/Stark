import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
import numpy as np
from typing import Dict, Any, List
import logging

class AdvancedThreatAnalyzer:
    def __init__(self):
        self.bert_model = self._initialize_bert()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.threat_classifier = self._build_classifier()
        self.logger = logging.getLogger(__name__)
        
    def _initialize_bert(self) -> BertModel:
        try:
            model = BertModel.from_pretrained('bert-base-uncased')
            for param in model.parameters():
                param.requires_grad = True
            return model
        except Exception as e:
            self.logger.error(f"Error initializing BERT model: {str(e)}")
            raise
        
    def _build_classifier(self) -> nn.Sequential:
        return nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 5)  # 5 threat levels
        )
    
    def analyze(self, text_data: str) -> Dict[str, Any]:
        try:
            # Tokenize input
            encoded = self.tokenizer(
                text_data,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            with torch.no_grad():
                # Get BERT embeddings
                outputs = self.bert_model(
                    input_ids=encoded['input_ids'],
                    attention_mask=encoded['attention_mask']
                )
                
                # Get pooled output
                pooled_output = outputs.pooler_output
                
                # Get threat classification
                threat_logits = self.threat_classifier(pooled_output)
                threat_probs = torch.softmax(threat_logits, dim=1)
                
            # Generate detailed analysis
            analysis_result = self._generate_detailed_analysis(threat_probs)
            
            return {
                'threat_probabilities': threat_probs.numpy().tolist(),
                'threat_level': self._get_threat_level(threat_probs),
                'confidence_score': float(torch.max(threat_probs).item()),
                'detailed_analysis': analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Error during threat analysis: {str(e)}")
            raise
    
    def _generate_detailed_analysis(self, probs: torch.Tensor) -> Dict[str, Any]:
        threat_levels = ['LOW', 'GUARDED', 'ELEVATED', 'HIGH', 'SEVERE']
        probs_np = probs.numpy()[0]
        
        return {
            'threat_distribution': {
                level: float(prob) 
                for level, prob in zip(threat_levels, probs_np)
            },
            'primary_threat_level': threat_levels[np.argmax(probs_np)],
            'confidence_metrics': {
                'entropy': float(-np.sum(probs_np * np.log(probs_np + 1e-10))),
                'max_probability': float(np.max(probs_np)),
                'probability_spread': float(np.max(probs_np) - np.mean(probs_np))
            },
            'recommendation': self._generate_recommendation(probs_np)
        }
    
    def _get_threat_level(self, probs: torch.Tensor) -> str:
        levels = ['LOW', 'GUARDED', 'ELEVATED', 'HIGH', 'SEVERE']
        max_prob_idx = torch.argmax(probs, dim=1)
        return levels[max_prob_idx]
    
    def _generate_recommendation(self, probs: np.ndarray) -> Dict[str, Any]:
        max_prob = np.max(probs)
        threat_level = ['LOW', 'GUARDED', 'ELEVATED', 'HIGH', 'SEVERE'][np.argmax(probs)]
        
        recommendations = {
            'SEVERE': ['Immediate action required', 'Isolate affected systems', 'Engage incident response team'],
            'HIGH': ['Escalate to security team', 'Increase monitoring', 'Prepare incident response'],
            'ELEVATED': ['Monitor closely', 'Review security logs', 'Update security rules'],
            'GUARDED': ['Regular monitoring', 'Update threat signatures', 'Document findings'],
            'LOW': ['Continue normal monitoring', 'Log for future reference']
        }
        
        return {
            'actions': recommendations[threat_level],
            'urgency': 'IMMEDIATE' if max_prob > 0.8 else 'HIGH' if max_prob > 0.6 else 'NORMAL',
            'confidence_level': 'HIGH' if max_prob > 0.8 else 'MEDIUM' if max_prob > 0.6 else 'LOW'
        }