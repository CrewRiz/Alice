"""Utility management for Alice system."""
import logging
from typing import List, Dict, Any
import numpy as np
from datetime import datetime

from config import REFERENCE_TIME, UTILITY_THRESHOLD

class UtilityManager:
    """Manages system utility calculations and optimization."""
    
    def __init__(self, desired_threshold: float = UTILITY_THRESHOLD):
        self.history: List[float] = []
        self.desired_threshold = desired_threshold
        self.reference_time = REFERENCE_TIME
        self.last_evaluation = self.reference_time
        self.weights = {
            'task_success': 0.4,
            'resource_efficiency': 0.3,
            'learning_efficiency': 0.2,
            'time_efficiency': 0.1
        }
        logging.info("UtilityManager initialized")
        
    def evaluate(self, state_manager: 'StateManager') -> float:
        """Calculate overall utility score with component weights."""
        try:
            # Get component scores
            scores = {
                'task_success': self.calculate_task_success_rate(state_manager),
                'resource_efficiency': self.calculate_resource_efficiency(state_manager),
                'learning_efficiency': self.calculate_learning_efficiency(state_manager),
                'time_efficiency': self.calculate_time_efficiency(state_manager)
            }
            
            # Calculate time-based decay
            time_delta = (self.reference_time - self.last_evaluation).total_seconds()
            decay_factor = np.exp(-0.01 * time_delta / 3600.0)  # Decay per hour
            
            # Calculate weighted sum
            utility = sum(
                self.weights[component] * score 
                for component, score in scores.items()
            ) * decay_factor
            
            # Update history
            self.history.append(utility)
            self.last_evaluation = self.reference_time
            
            # Log detailed evaluation
            logging.info(
                f"Utility evaluated: {utility:.4f} (decay_factor: {decay_factor:.4f})\n"
                f"Component scores: {scores}"
            )
            
            return utility
            
        except Exception as e:
            logging.error(f"Error evaluating utility: {str(e)}", exc_info=True)
            return 0.0
            
    def calculate_task_success_rate(self, state_manager: 'StateManager') -> float:
        """Calculate task success rate with error handling."""
        try:
            completed = state_manager.metrics.get('completed_tasks', 0)
            total = state_manager.metrics.get('total_tasks', 1)
            success_rate = completed / total if total > 0 else 0.0
            logging.debug(f"Task success rate: {success_rate:.4f}")
            return success_rate
        except Exception as e:
            logging.error(f"Error calculating task success rate: {str(e)}")
            return 0.0
            
    def calculate_resource_efficiency(self, state_manager: 'StateManager') -> float:
        """Calculate resource efficiency score."""
        try:
            cpu_usage = state_manager.metrics.get('cpu_usage', 1.0)
            memory_usage = state_manager.metrics.get('memory_usage', 1.0)
            
            # Lower resource usage is better
            efficiency = 1.0 - (0.5 * cpu_usage + 0.5 * memory_usage)
            logging.debug(f"Resource efficiency: {efficiency:.4f}")
            return efficiency
        except Exception as e:
            logging.error(f"Error calculating resource efficiency: {str(e)}")
            return 0.0
            
    def calculate_learning_efficiency(self, state_manager: 'StateManager') -> float:
        """Calculate learning and adaptation efficiency."""
        try:
            new_rules = state_manager.metrics.get('new_rules_generated', 0)
            total_rules = len(state_manager.active_rules)
            
            if total_rules > 0:
                efficiency = new_rules / total_rules
            else:
                efficiency = 0.0
                
            logging.debug(f"Learning efficiency: {efficiency:.4f}")
            return efficiency
        except Exception as e:
            logging.error(f"Error calculating learning efficiency: {str(e)}")
            return 0.0
            
    def calculate_time_efficiency(self, state_manager: 'StateManager') -> float:
        """Calculate time-based efficiency metrics."""
        try:
            avg_task_time = state_manager.metrics.get('average_task_time', 1.0)
            target_time = 0.5  # Target completion time in seconds
            
            # Use exponential decay for time efficiency
            efficiency = np.exp(-abs(avg_task_time - target_time))
            logging.debug(f"Time efficiency: {efficiency:.4f}")
            return efficiency
        except Exception as e:
            logging.error(f"Error calculating time efficiency: {str(e)}")
            return 0.0
            
    def get_utility_history(self, count: int = 10) -> List[float]:
        """Get recent utility history."""
        return self.history[-count:]
        
    def needs_improvement(self) -> bool:
        """Check if system needs improvement based on utility threshold."""
        if not self.history:
            return False
        return self.history[-1] < self.desired_threshold
        
    def adjust_weights(self, new_weights: Dict[str, float]) -> None:
        """Adjust component weights for utility calculation."""
        # Validate weights sum to 1.0
        if abs(sum(new_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0")
            
        self.weights = new_weights.copy()
        logging.info(f"Utility weights adjusted: {self.weights}")
