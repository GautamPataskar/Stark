import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Generate log filename with timestamp
log_filename = f"logs/stark_ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s", "extra": %(extra)s}'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': log_filename,
            'mode': 'a'
        },
        'json_file': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.FileHandler',
            'filename': f"logs/stark_ml_json_{datetime.now().strftime('%Y%m%d')}.log",
            'mode': 'a'
        },
        'error_file': {
            'level': 'ERROR',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': f"logs/stark_ml_error_{datetime.now().strftime('%Y%m%d')}.log",
            'mode': 'a'
        }
    },
    'loggers': {
        'STARK.ML': {
            'handlers': ['console', 'file', 'json_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'STARK.ML.models': {
            'handlers': ['console', 'file', 'json_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'STARK.ML.preprocessing': {
            'handlers': ['console', 'file', 'json_file'],
            'level': 'INFO',
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}