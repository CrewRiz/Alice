import random
import numpy as np
import networkx as nx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class Rule:
    def __init__(self, condition: str, action: str, strength: float = 1.0):
        self.condition = condition
        self.action = action
        self.strength = strength
        self.confidence = 1.0
        self.usage_count = 0

class Gene:
    def __init__(self, rules=None, priority=1.0, metadata=None):
        self.rules = rules or []  # List of Rule objects
        self.priority = priority
        self.metadata = metadata or {}
        self.fitness = 1.0
        self.expression_level = 1.0  # Controls gene activation
        self.regulatory_factors = {}  # Factors affecting expression
        self.network_connections = []  # Connected genes
        self.mutation_rate = 0.1
        self.creation_time = datetime.fromisoformat("2024-12-23T03:31:30-06:00")
        
    def add_rule(self, rule):
        if isinstance(rule, Rule):
            self.rules.append(rule)
            
    def remove_rule(self, rule):
        if rule in self.rules:
            self.rules.remove(rule)
            
    def calculate_fitness(self, metrics):
        """Calculate gene fitness based on rule performance"""
        if not self.rules:
            return 0.0
        rule_fitness = sum(rule.strength * rule.confidence for rule in self.rules)
        self.fitness = (rule_fitness / len(self.rules)) * self.priority * self.expression_level
        return self.fitness
        
    def mutate(self):
        """Introduce random variations in gene properties"""
        if random.random() < self.mutation_rate:
            self.priority *= random.uniform(0.8, 1.2)
            for rule in self.rules:
                if random.random() < self.mutation_rate:
                    rule.strength *= random.uniform(0.9, 1.1)
                    
    def update_expression(self, context):
        """Update gene expression level based on regulatory factors"""
        factor_influence = sum(self.regulatory_factors.values())
        self.expression_level = 1.0 / (1.0 + np.exp(-factor_influence))  # Sigmoid activation
        
    def decay(self, current_time: datetime, decay_rate=0.05):
        """Apply time-based decay to gene properties"""
        time_delta = (current_time - self.creation_time).total_seconds()
        time_factor = np.exp(-decay_rate * time_delta / 86400.0)  # Normalize to days
        self.priority *= time_factor

class GeneticRuleSystem:
    def __init__(self, population_size=100):
        self.genes: List[Gene] = []
        self.population_size = population_size
        self.generation = 0
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = int(population_size * 0.1)
        self.gene_network = nx.DiGraph()
        self.creation_time = datetime.fromisoformat("2024-12-23T03:31:30-06:00")
        
    def add_gene(self, gene: Gene):
        self.genes.append(gene)
        self.gene_network.add_node(gene)
        
    def remove_gene(self, gene: Gene):
        if gene in self.genes:
            self.genes.remove(gene)
            self.gene_network.remove_node(gene)
        
    def crossover(self, parent1: Gene, parent2: Gene) -> Gene:
        """Perform crossover between two parent genes"""
        if random.random() < self.crossover_rate:
            # Mix rules from both parents
            child_rules = random.sample(parent1.rules, len(parent1.rules)//2)
            child_rules.extend(random.sample(parent2.rules, len(parent2.rules)//2))
            
            # Average priorities and combine metadata
            child_priority = (parent1.priority + parent2.priority) / 2
            child_metadata = {**parent1.metadata, **parent2.metadata}
            
            return Gene(child_rules, child_priority, child_metadata)
        return random.choice([parent1, parent2])
        
    def select_parents(self) -> Gene:
        """Select parents using tournament selection"""
        if not self.genes:
            return Gene()  # Return empty gene if no population
        tournament_size = min(5, len(self.genes))
        tournament = random.sample(self.genes, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
        
    def evolve(self, metrics: Dict[str, Any]):
        """Evolve the population for one generation"""
        if not self.genes:
            return
            
        # Calculate fitness for all genes
        for gene in self.genes:
            gene.calculate_fitness(metrics)
            
        # Sort by fitness
        self.genes.sort(key=lambda x: x.fitness, reverse=True)
        
        # Keep elite individuals
        new_population = self.genes[:self.elite_size]
        
        # Create rest of new population
        while len(new_population) < self.population_size:
            parent1 = self.select_parents()
            parent2 = self.select_parents()
            child = self.crossover(parent1, parent2)
            child.mutate()
            new_population.append(child)
            
        self.genes = new_population
        self.generation += 1
        
    def update_network(self):
        """Update gene network connections based on interactions"""
        for gene1 in self.genes:
            for gene2 in self.genes:
                if gene1 != gene2:
                    interaction = self._calculate_interaction(gene1, gene2)
                    if interaction > 0:
                        self.gene_network.add_edge(gene1, gene2, weight=interaction)
                        
    def _calculate_interaction(self, gene1: Gene, gene2: Gene) -> float:
        """Calculate interaction strength between two genes"""
        shared_factors = set(gene1.regulatory_factors.keys()) & set(gene2.regulatory_factors.keys())
        if not shared_factors:
            return 0.0
        
        interaction = sum(gene1.regulatory_factors[f] * gene2.regulatory_factors[f] for f in shared_factors)
        return max(0.0, min(1.0, interaction))
