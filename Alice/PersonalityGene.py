import Gene

class PersonalityGene(Gene):
    def __init__(self, trait_type, initial_value=0.5):
        super().__init__(rules=None)
        self.trait_type = trait_type  # e.g. 'openness', 'conscientiousness'
        self.value = initial_value
        self.expression_modifiers = {}
        self.learning_rate = 0.1
        
    def adapt(self, experience):
        """Adapt trait value based on experience"""
        self.value += self.learning_rate * experience
        self.value = max(0.0, min(1.0, self.value))

class PersonalitySystem:
    def __init__(self, name="Alice"):
        self.name = name
        self.traits = {
            # OCEAN model
            'openness': PersonalityGene('openness', 0.7),
            'conscientiousness': PersonalityGene('conscientiousness', 0.8), 
            'extraversion': PersonalityGene('extraversion', 0.6),
            'agreeableness': PersonalityGene('agreeableness', 0.7),
            'neuroticism': PersonalityGene('neuroticism', 0.4),
            
            # Additional traits
            'curiosity': PersonalityGene('curiosity', 0.8),
            'creativity': PersonalityGene('creativity', 0.7),
            'empathy': PersonalityGene('empathy', 0.6)
        }
        
        self.mood = {
            'pleasure': 0.5,
            'arousal': 0.5,
            'dominance': 0.5
        }
        
        self.memories = deque(maxlen=1000)
        self.personality_network = nx.DiGraph()
        self._build_trait_network()
        
    def _build_trait_network(self):
        """Build network of trait interactions"""
        for t1 in self.traits:
            self.personality_network.add_node(t1)
            for t2 in self.traits:
                if t1 != t2:
                    weight = random.uniform(-0.5, 0.5)
                    self.personality_network.add_edge(t1, t2, weight=weight)
                    
    def update_from_experience(self, experience):
        """Update personality based on experience"""
        # Update traits
        for trait in self.traits.values():
            relevant_exp = experience.get(trait.trait_type, 0)
            trait.adapt(relevant_exp)
            
        # Update mood
        self.mood['pleasure'] += experience.get('pleasure', 0)
        self.mood['arousal'] += experience.get('arousal', 0)
        self.mood['dominance'] += experience.get('dominance', 0)
        
        # Normalize mood values
        for k in self.mood:
            self.mood[k] = max(0.0, min(1.0, self.mood[k]))
            
        # Store experience
        self.memories.append(experience)
        
        # Update trait network
        self._update_trait_network()
        
    def _update_trait_network(self):
        """Update trait relationships based on experiences"""
        for t1, t2 in self.personality_network.edges():
            correlation = self._calculate_trait_correlation(t1, t2)
            self.personality_network[t1][t2]['weight'] *= 0.9  # Decay
            self.personality_network[t1][t2]['weight'] += 0.1 * correlation
            
    def get_response_modulation(self, response_type):
        """Modulate responses based on personality"""
        modulation = {
            'content': 1.0,
            'style': 1.0,
            'emotion': 1.0
        }
        
        # Adjust content based on openness and conscientiousness
        modulation['content'] *= (0.5 + self.traits['openness'].value)
        modulation['content'] *= (0.5 + self.traits['conscientiousness'].value)
        
        # Adjust style based on extraversion and agreeableness 
        modulation['style'] *= (0.5 + self.traits['extraversion'].value)
        modulation['style'] *= (0.5 + self.traits['agreeableness'].value)
        
        # Adjust emotion based on neuroticism and empathy
        modulation['emotion'] *= (0.5 + self.traits['neuroticism'].value)
        modulation['emotion'] *= (0.5 + self.traits['empathy'].value)
        
        return modulation[response_type]
        
    def get_personality_summary(self):
        """Get current personality state summary"""
        return {
            'traits': {k: v.value for k, v in self.traits.items()},
            'mood': self.mood,
            'trait_relationships': dict(self.personality_network.edges(data=True))
        }




