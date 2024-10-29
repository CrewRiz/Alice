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
        self.creation_time = time.time()
        
    def add_rule(self, rule):
        if isinstance(rule, Rule):
            self.rules.append(rule)
            
    def remove_rule(self, rule):
        if rule in self.rules:
            self.rules.remove(rule)
            
    def calculate_fitness(self, metrics):
        """Calculate gene fitness based on rule performance"""
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
        
    def decay(self, current_time, decay_rate=0.05):
        """Apply time-based decay to gene properties"""
        time_factor = np.exp(-decay_rate * (current_time - self.creation_time))
        self.priority *= time_factor

class GeneticRuleSystem:
    def __init__(self, population_size=100):
        self.genes = []
        self.population_size = population_size
        self.generation = 0
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = int(population_size * 0.1)
        self.gene_network = nx.DiGraph()
        
    def add_gene(self, gene):
        self.genes.append(gene)
        self.gene_network.add_node(gene)
        
    def remove_gene(self, gene):
        self.genes.remove(gene)
        self.gene_network.remove_node(gene)
        
    def crossover(self, parent1, parent2):
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
        
    def select_parents(self):
        """Select parents using tournament selection"""
        tournament_size = 5
        tournament = random.sample(self.genes, tournament_size)
        return max(tournament, key=lambda x: x.fitness)
        
    def evolve(self, metrics):
        """Evolve the population for one generation"""
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
        
        # Update gene network
        self._update_gene_network()
        
    def _update_gene_network(self):
        """Update gene regulatory network based on interactions"""
        self.gene_network.clear()
        for gene in self.genes:
            self.gene_network.add_node(gene)
            for other_gene in self.genes:
                if gene != other_gene:
                    # Calculate interaction strength based on rule similarities
                    interaction = self._calculate_interaction(gene, other_gene)
                    if interaction > 0:
                        self.gene_network.add_edge(gene, other_gene, weight=interaction)
                        
    def _calculate_interaction(self, gene1, gene2):
        """Calculate interaction strength between two genes"""
        # Simple similarity metric based on rule overlap
        rules1 = set(gene1.rules)
        rules2 = set(gene2.rules)
        overlap = len(rules1.intersection(rules2))
        return overlap / max(len(rules1), len(rules2))
        
    def update_regulatory_factors(self):
        """Update regulatory factors based on network structure"""
        for gene in self.genes:
            incoming = self.gene_network.in_edges(gene, data=True)
            regulatory_sum = sum(data['weight'] for _, _, data in incoming)
            gene.regulatory_factors['network'] = regulatory_sum
            gene.update_expression({})


