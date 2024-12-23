"""State management for Alice system."""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import networkx as nx
import numpy as np

from config import REFERENCE_TIME, DEFAULT_EMOTIONS, get_system_metrics

class StateManager:
    """Manages system state with time-based decay and error handling."""
    
    def __init__(self):
        self.reference_time = REFERENCE_TIME
        self.metrics = get_system_metrics()
        self.active_rules: List[Dict[str, Any]] = []
        self.pending_actions: List[Dict[str, Any]] = []
        self.knowledge_graph: nx.DiGraph = nx.DiGraph()
        self.current_task: Optional[str] = None
        self.past_interactions: List[Dict[str, Any]] = []
        self.emotions = DEFAULT_EMOTIONS.copy()
        self.operational_state = {
            'status': 'ready',
            'last_update': self.reference_time,
            'error_count': 0
        }
        logging.info("StateManager initialized")
        
    def update(self, new_data: Dict[str, Any]) -> None:
        """Update system state with time-based decay."""
        try:
            # Calculate time-based decay
            time_delta = (self.reference_time - self.operational_state['last_update']).total_seconds()
            decay_factor = np.exp(-0.1 * time_delta / 3600.0)  # Decay per hour
            
            # Update metrics
            self._update_metrics(new_data, decay_factor)
            
            # Update emotions
            self._update_emotions(new_data, decay_factor)
            
            # Update operational state
            self._update_operational_state(new_data)
            
            logging.info(f"State updated successfully with decay_factor: {decay_factor:.4f}")
            
        except Exception as e:
            self.operational_state['error_count'] += 1
            logging.error(f"Error updating system state: {str(e)}", exc_info=True)
            raise
            
    def _update_metrics(self, new_data: Dict[str, Any], decay_factor: float) -> None:
        """Update system metrics with decay."""
        for key, value in new_data.items():
            if key in self.metrics:
                if isinstance(value, (int, float)):
                    self.metrics[key] = value * decay_factor
                else:
                    self.metrics[key] = value
                    
    def _update_emotions(self, new_data: Dict[str, Any], decay_factor: float) -> None:
        """Update emotional state with decay."""
        for emotion in self.emotions:
            # Apply decay
            self.emotions[emotion] *= decay_factor
            
            # Add new emotion values if present
            if emotion in new_data.get('emotions', {}):
                self.emotions[emotion] += new_data['emotions'][emotion]
                
            # Clamp values between 0 and 1
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
            
    def _update_operational_state(self, new_data: Dict[str, Any]) -> None:
        """Update operational state."""
        self.operational_state['last_update'] = self.reference_time
        self.operational_state['status'] = new_data.get('status', self.operational_state['status'])
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current system state."""
        return {
            'metrics': self.metrics,
            'emotions': self.emotions,
            'operational_state': self.operational_state,
            'current_task': self.current_task,
            'pending_actions_count': len(self.pending_actions),
            'active_rules_count': len(self.active_rules),
            'knowledge_graph_size': len(self.knowledge_graph)
        }
        
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """Add a new interaction to history."""
        interaction['timestamp'] = self.reference_time
        self.past_interactions.append(interaction)
        
        # Trim history if too long
        if len(self.past_interactions) > 1000:
            self.past_interactions = self.past_interactions[-1000:]
            
    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent interactions."""
        return self.past_interactions[-count:]
        
    def clear_pending_actions(self) -> None:
        """Clear all pending actions."""
        self.pending_actions.clear()
        
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a new rule to active rules."""
        rule['added_time'] = self.reference_time
        self.active_rules.append(rule)
        self.metrics['new_rules_generated'] += 1
