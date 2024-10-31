# Alice: Self-Learning Godel Agent

Alice is a sophisticated AI-driven framework designed for autonomous task management and execution. It leverages rule-based interactions, knowledge management, and web integration to learn, adapt, and execute complex tasks, using powerful libraries like OpenAI, Anthropic, Streamlit, Selenium, and FAISS. Alice maintains a persistent state across sessions, providing a robust and adaptive learning environment.

At a high level, Alice is designed as a self-learning agent that integrates a range of capabilities to operate autonomously. Its core features—such as rule-based processing, knowledge management, pattern detection, and web interaction—allow it to learn, make decisions, and complete tasks without extensive user guidance. Alice combines traditional automation with elements of reinforcement learning and novelty seeking to continuously refine its rule set, improving how it completes tasks and responds to new information over time.

High-Level Overview of Alice's Functionality
Rule-Based Decision Making: Alice follows a dynamic set of rules to decide its actions. These rules are initially defined by the user but are also generated and modified by the agent itself as it learns from patterns in its environment.

Knowledge Management and Memory: Using FAISS, Alice builds a knowledge base, allowing it to retrieve and apply relevant information to ongoing tasks. This memory system enables it to "remember" past interactions, making it more adaptive and informed in its responses.

Pattern Detection and Rule Generation: Alice can detect patterns in data, enabling it to create new rules or refine existing ones autonomously. This learning process helps Alice improve over time, becoming more efficient and responsive.

Web Interaction: Through Selenium, Alice can interact with the internet autonomously, browsing pages, gathering information, and integrating new data into its knowledge base. This feature makes it versatile in real-world applications, from simple data gathering to more complex web-based interactions.

User Interface and Feedback Mechanism: The Streamlit interface allows users to interact with Alice in a meaningful way, providing input, monitoring progress, and viewing results, all while giving the agent feedback that can further refine its learning.

Innovative Approach to Agents
Alice takes a unique approach by combining traditional rule-based AI with learning and self-adaptation through pattern recognition and novelty-seeking mechanisms. Unlike conventional agents that rely solely on either static rules or predefined models, Alice creates a blend:

Hybrid Rule and Learning System: Instead of relying purely on machine learning, Alice’s use of rule-based decision-making gives it a structured way to operate that’s familiar to traditional AI, while the integration of pattern-based rule generation provides flexibility to adapt.

Knowledge-Driven Adaptation: The memory retrieval and similarity search with FAISS provide a persistent knowledge base, making Alice capable of adapting its behavior based on past experiences and helping it understand context over time.

Self-Generating Capabilities: The self-updating rules and dynamically created actions mark an innovative twist, enabling Alice to adapt as its understanding of the environment deepens. The agent’s ability to create and modify rules based on detected patterns is somewhat novel for autonomous agents.

Exploration-Based Learning: Through its novelty-seeking behavior, Alice ventures into new data and ideas, going beyond predefined tasks to explore adjacent knowledge. This enhances Alice’s versatility, making it capable of functioning in less structured environments than many agents typically handle.

In sum, Alice is positioned as a forward-looking agent that brings a practical fusion of static rules and adaptive learning. This approach is innovative because it leverages the best of rule-based systems while incorporating self-adaptive and exploratory elements to enhance its autonomy, making it a powerful tool for complex, real-world applications.



## Features

- **Rule-Based System**: Define actions based on specific conditions.
- **Knowledge Management**: Utilize FAISS for similarity search and memory retrieval.
- **Computer Interaction**: Automate interactions using `pyautogui` and `selenium`.
- **Persistent Storage**: Maintain state, rules, and knowledge graphs across sessions.
- **Pattern Detection & Rule Generation**: Generate new rules dynamically using AI agents.
- **System Analysis**: Monitor metrics for optimal performance.
- **Novelty Seeking**: Expand the knowledge base by seeking new information.
- **User Interface**: Engage with Alice via a Streamlit web interface.

## Architecture

Alice is modular, with each component responsible for specific functionalities:
- **Rule**: Defines the structure of system rules.
- **KnowledgeNode**: Represents nodes in the knowledge graph.
- **ComputerInteractionSystem**: Manages automated computer interactions.
- **RAGMemory**: Manages memory using Retrieval-Augmented Generation.
- **SystemState**: Maintains system state and metrics.
- **PatternDetectionAgent**: Detects patterns in data.
- **RuleGenerationAgent**: Generates new rules.
- **AnalysisAgent**: Recommends actions based on system state.
- **WebInteractionAgent**: Manages browsing and web interactions.
- **NoveltySeekingAlgorithm**: Expands knowledge by seeking novel data.
- **PersistentStorage**: Manages data storage and retrieval.
- **EnhancedLearningSystem**: Integrates all components for a cohesive learning environment.

## Installation

### Prerequisites
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Chrome Browser**: Required for Selenium WebDriver. [Download Chrome](https://www.google.com/chrome/)

### Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/CrewRiz/Alice.git
   cd Alice





 
