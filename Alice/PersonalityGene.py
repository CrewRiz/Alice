import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum, auto

from TimePerception import QuantumTime
from Gene import GeneticRuleSystem

@dataclass
class EmotionalState:
    joy: float = 0.5
    trust: float = 0.5
    fear: float = 0.2
    surprise: float = 0.3
    decay_rate: float = 0.1
    last_update: datetime = datetime.fromisoformat("2024-12-23T03:36:57-06:00")

    def update(self, new_state: Dict[str, float], current_time: datetime):
        time_delta = (current_time - self.last_update).total_seconds()
        decay_factor = np.exp(-self.decay_rate * time_delta / 3600.0)
        
        self.joy = self.joy * decay_factor + new_state.get('joy', 0) * (1 - decay_factor)
        self.trust = self.trust * decay_factor + new_state.get('trust', 0) * (1 - decay_factor)
        self.fear = self.fear * decay_factor + new_state.get('fear', 0) * (1 - decay_factor)
        self.surprise = self.surprise * decay_factor + new_state.get('surprise', 0) * (1 - decay_factor)
        
        self.last_update = current_time

class TraitType(Enum):
    OPENNESS = auto()
    CONSCIENTIOUSNESS = auto()
    EXTRAVERSION = auto()
    AGREEABLENESS = auto()
    NEUROTICISM = auto()
    CREATIVITY = auto()
    RATIONALITY = auto()
    EMPATHY = auto()

@dataclass
class PersonalityTrait:
    trait_type: TraitType
    value: float
    confidence: float
    last_update: datetime
    quantum_phase: float = 0.0
    entanglement_partners: List[TraitType] = None
    
    def __post_init__(self):
        if self.entanglement_partners is None:
            self.entanglement_partners = []

class PersonalitySystem:
    def __init__(self):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:36:57-06:00")
        self.emotional_state = EmotionalState()
        self.traits: Dict[TraitType, PersonalityTrait] = self._initialize_traits()
        self.trait_network = nx.Graph()
        self.quantum_time = QuantumTime()
        self.genetic_system = GeneticRuleSystem()
        self._build_trait_network()
        
        logging.info("PersonalitySystem initialized with quantum integration")

    def _initialize_traits(self) -> Dict[TraitType, PersonalityTrait]:
        return {
            trait_type: PersonalityTrait(
                trait_type=trait_type,
                value=0.5,
                confidence=0.8,
                last_update=self.reference_time,
                quantum_phase=np.random.uniform(0, 2 * np.pi)
            )
            for trait_type in TraitType
        }

    def _build_trait_network(self):
        # Define trait relationships with quantum considerations
        relationships = [
            (TraitType.OPENNESS, TraitType.CREATIVITY, 0.8),
            (TraitType.CONSCIENTIOUSNESS, TraitType.RATIONALITY, 0.7),
            (TraitType.EXTRAVERSION, TraitType.EMPATHY, 0.6),
            (TraitType.AGREEABLENESS, TraitType.EMPATHY, 0.8),
            (TraitType.NEUROTICISM, TraitType.RATIONALITY, -0.4),
            (TraitType.CREATIVITY, TraitType.RATIONALITY, 0.3),
            (TraitType.EMPATHY, TraitType.RATIONALITY, 0.5)
        ]
        
        for t1, t2, weight in relationships:
            self.trait_network.add_edge(t1, t2, weight=weight)
            self.traits[t1].entanglement_partners.append(t2)
            self.traits[t2].entanglement_partners.append(t1)

    def update_from_experience(self, experience: Dict[str, Any]):
        current_time = self.reference_time
        quantum_phase = self.quantum_time.get_current_phase()
        
        # Update emotional state
        emotional_impact = self._calculate_emotional_impact(experience)
        self.emotional_state.update(emotional_impact, current_time)
        
        # Update traits with quantum effects
        for trait_type, trait in self.traits.items():
            # Calculate time-based decay
            time_delta = (current_time - trait.last_update).total_seconds()
            base_decay = np.exp(-0.1 * time_delta / 3600.0)
            
            # Apply quantum phase modulation
            phase_diff = abs(trait.quantum_phase - quantum_phase)
            quantum_modifier = np.cos(phase_diff) * 0.2 + 0.8  # Range: [0.6, 1.0]
            
            # Calculate entanglement effects
            entanglement_effect = self._calculate_entanglement_effect(trait_type)
            
            # Update trait value with all effects combined
            experience_value = experience.get(trait_type.name.lower(), 0.0)
            trait.value = (
                trait.value * base_decay * quantum_modifier +
                experience_value * (1 - base_decay) +
                entanglement_effect
            )
            
            # Update quantum properties
            trait.quantum_phase = (trait.quantum_phase + phase_diff * 0.1) % (2 * np.pi)
            trait.last_update = current_time
            
            # Update confidence based on consistency of experiences
            trait.confidence = min(1.0, trait.confidence + 0.1 * base_decay)

    def _calculate_emotional_impact(self, experience: Dict[str, Any]) -> Dict[str, float]:
        success_rate = experience.get('task_success', 0.5)
        novelty = experience.get('novelty', 0.0)
        complexity = experience.get('complexity', 0.5)
        
        return {
            'joy': success_rate * 0.7 + novelty * 0.3,
            'trust': success_rate * 0.6 + (1 - complexity) * 0.4,
            'fear': complexity * 0.5 + (1 - success_rate) * 0.5,
            'surprise': novelty * 0.8 + complexity * 0.2
        }

    def _calculate_entanglement_effect(self, trait_type: TraitType) -> float:
        if not self.traits[trait_type].entanglement_partners:
            return 0.0
            
        total_effect = 0.0
        for partner_type in self.traits[trait_type].entanglement_partners:
            partner_trait = self.traits[partner_type]
            edge_weight = self.trait_network[trait_type][partner_type]['weight']
            
            # Calculate quantum correlation
            phase_correlation = np.cos(partner_trait.quantum_phase - self.traits[trait_type].quantum_phase)
            
            # Combine classical and quantum effects
            effect = edge_weight * partner_trait.value * phase_correlation * 0.1
            total_effect += effect
            
        return total_effect / len(self.traits[trait_type].entanglement_partners)

    def get_response_modulation(self, context: str) -> Dict[str, float]:
        """Calculate personality-based response modulation factors."""
        modulation = {
            'creativity': self.traits[TraitType.CREATIVITY].value,
            'rationality': self.traits[TraitType.RATIONALITY].value,
            'empathy': self.traits[TraitType.EMPATHY].value,
            'confidence': np.mean([trait.confidence for trait in self.traits.values()]),
            'emotional_state': {
                'joy': self.emotional_state.joy,
                'trust': self.emotional_state.trust,
                'fear': self.emotional_state.fear,
                'surprise': self.emotional_state.surprise
            }
        }
        
        # Apply quantum phase effects
        current_phase = self.quantum_time.get_current_phase()
        phase_modifier = np.cos(current_phase) * 0.2 + 0.8
        
        for key in ['creativity', 'rationality', 'empathy']:
            modulation[key] *= phase_modifier
            
        return modulation

    def get_trait_summary(self) -> Dict[str, Any]:
        """Get a summary of current personality traits and emotional state."""
        return {
            'traits': {
                trait_type.name: {
                    'value': trait.value,
                    'confidence': trait.confidence,
                    'quantum_phase': trait.quantum_phase
                }
                for trait_type, trait in self.traits.items()
            },
            'emotional_state': {
                'joy': self.emotional_state.joy,
                'trust': self.emotional_state.trust,
                'fear': self.emotional_state.fear,
                'surprise': self.emotional_state.surprise
            },
            'last_update': self.reference_time.isoformat()
        }

    def adapt_to_feedback(self, feedback: Dict[str, float]):
        """Adapt personality traits based on external feedback."""
        current_time = self.reference_time
        quantum_phase = self.quantum_time.get_current_phase()
        
        for trait_type, trait in self.traits.items():
            if trait_type.name.lower() in feedback:
                feedback_value = feedback[trait_type.name.lower()]
                
                # Calculate adaptation rate based on quantum phase alignment
                phase_alignment = np.cos(trait.quantum_phase - quantum_phase)
                adaptation_rate = 0.2 * (1 + phase_alignment)
                
                # Update trait value with quantum-influenced adaptation
                trait.value = trait.value * (1 - adaptation_rate) + feedback_value * adaptation_rate
                trait.quantum_phase = (trait.quantum_phase + phase_alignment * 0.1) % (2 * np.pi)
                trait.last_update = current_time
                
                # Update confidence based on feedback consistency
                previous_value = trait.value
                value_diff = abs(previous_value - feedback_value)
                confidence_change = -0.1 if value_diff > 0.3 else 0.1
                trait.confidence = max(0.1, min(1.0, trait.confidence + confidence_change))
                
        self._update_trait_network(feedback)

    def _update_trait_network(self, feedback: Dict[str, float]):
        # Update trait relationships based on feedback
        for trait_type, trait in self.traits.items():
            if trait_type.name.lower() in feedback:
                feedback_value = feedback[trait_type.name.lower()]
                
                # Update entanglement partners
                for partner_type in trait.entanglement_partners:
                    partner_trait = self.traits[partner_type]
                    edge_weight = self.trait_network[trait_type][partner_type]['weight']
                    
                    # Calculate quantum correlation
                    phase_correlation = np.cos(partner_trait.quantum_phase - trait.quantum_phase)
                    
                    # Update edge weight based on feedback and quantum correlation
                    new_weight = edge_weight + feedback_value * phase_correlation * 0.1
                    self.trait_network[trait_type][partner_type]['weight'] = new_weight
