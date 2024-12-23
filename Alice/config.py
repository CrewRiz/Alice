"""Configuration settings for Alice system."""
import os
from datetime import datetime
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Core time reference
REFERENCE_TIME = datetime.now()

# API Keys (loaded from environment variables)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# System Parameters
UTILITY_THRESHOLD = 0.8
TIME_LIMITS = {
    'reasoning': 5.0,
    'self_improvement': 10.0,
    'task_execution': 30.0
}

# Emotion Parameters
DEFAULT_EMOTIONS = {
    'joy': 0.5,
    'trust': 0.6,
    'fear': 0.2,
    'surprise': 0.3
}

# Resource Usage
DEFAULT_RESOURCE_METRICS = {
    'cpu_usage': 0.5,
    'memory_usage': 0.5
}

# Logging Configuration
LOG_CONFIG = {
    'filename': 'alice.log',
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

def setup_logging():
    """Configure logging for the system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('alice.log')
        ]
    )
    
def get_system_metrics() -> Dict[str, Any]:
    """Get default system metrics."""
    return {
        'complexity': 0,
        'novelty': 0,
        'confidence': 1.0,
        'resource_usage': {},
        'completed_tasks': 0,
        'total_tasks': 0,
        **DEFAULT_RESOURCE_METRICS,
        'new_rules_generated': 0,
        'average_task_time': 1.0
    }
