Overview
Alice is a sophisticated AI-driven framework designed to autonomously manage and execute tasks through rule-based interactions, knowledge management, and web interactions. Leveraging powerful libraries and APIs such as OpenAI, Anthropic, Streamlit, Selenium, and FAISS, Alice is capable of learning, adapting, and executing complex tasks while maintaining a persistent state across sessions.

Features
Rule-Based System: Define and manage rules that dictate system actions based on specific conditions.
Knowledge Management: Utilize FAISS for efficient similarity search and embedding-based memory retrieval.
Computer Interaction: Automate mouse movements, clicks, typing, command execution, and web browsing using pyautogui and selenium.
Persistent Storage: Maintain system state, rules, memories, and knowledge graphs across sessions.
Pattern Detection and Rule Generation: Analyze data to detect patterns and generate new rules dynamically using AI agents.
System Analysis: Continuously monitor and analyze system metrics to optimize performance.
Novelty Seeking: Implement algorithms to seek new information and enhance the system’s knowledge base.
User Interface: Interact with Alice through an intuitive Streamlit web interface.
Architecture
Alice is composed of several interconnected classes and modules, each responsible for specific functionalities:

Rule: Defines the structure and behavior of system rules.
KnowledgeNode: Represents nodes in the knowledge graph with associated rules.
ComputerInteractionSystem: Handles automated interactions with the computer environment.
RAGMemory: Manages memory using Retrieval-Augmented Generation with FAISS for embedding-based searches.
SystemState: Maintains the current state and metrics of the system.
PatternDetectionAgent: Detects patterns in data using AI models.
RuleGenerationAgent: Generates new rules based on detected patterns.
AnalysisAgent: Analyzes the system state to recommend actions.
WebInteractionAgent: Manages web interactions and browsing.
NoveltySeekingAlgorithm: Enhances the system’s knowledge by seeking novel information.
PersistentStorage: Handles saving and loading of persistent data.
EnhancedLearningSystem: Integrates all components to provide a cohesive learning and execution environment.
Streamlit Interface: Provides a user-friendly web interface for interacting with Alice.
Installation
Prerequisites
Python 3.8+: Ensure Python is installed on your system. Download from python.org.
Chrome Browser: Required for Selenium WebDriver. Download from google.com/chrome.
Clone the Repository
git clone https://github.com/yourusername/alice-enhanced-learning-system.git
cd alice-enhanced-learning-system
Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
Install WebDriver
Download the Chrome WebDriver that matches your Chrome browser version from here and place it in your system's PATH or specify its location in the code.

Configuration
API Keys
Alice utilizes APIs from OpenAI and Anthropic. You need to obtain API keys and configure them in the system.

OpenAI API Key: Sign up at OpenAI to get your API key.
Anthropic API Key: Sign up at Anthropic to get your API key.
Setting API Keys
You can set the API keys as environment variables or directly in the code (not recommended for security reasons).

Using Environment Variables:


export OPENAI_API_KEY='your-openai-api-key'
export ANTHROPIC_API_KEY='your-anthropic-api-key'
Alternatively, set them directly in the code:


self.claude_client = anthropic.Client(api_key="your_anthropic_key")
self.openai_client = openai
openai.api_key = "your_openai_key"
Configuration File
Alice uses a default configuration for safety and operational limits. You can customize these settings by modifying the config parameter when initializing ComputerInteractionSystem.

Usage
Running the Application
Start the Streamlit interface to interact with Alice.
streamlit run alice.py

Using the Interface
Task Input: Enter a task description in the provided text area and click "Process Task" to initiate processing.
System Metrics: View real-time metrics of Alice, including complexity, novelty, confidence, and resource usage.
Results: After processing, Alice will display the updated system state and metrics.
Example Workflow
Input Task: Describe a task, such as "Automate the backup of important files."
Process Task: Click "Process Task" to let Alice analyze, generate rules, and execute necessary actions.
View Results: Monitor the system state and metrics to understand how the task was handled.
Components
Rule Class
Defines the structure of a rule, including its text, associated action, usage metrics, embedding for similarity, and connections to other rules.

KnowledgeNode Class
Represents nodes in the knowledge graph, linking rules and tracking their strength and entanglements.

ComputerInteractionSystem Class
Handles automated interactions with the computer, including mouse movements, clicks, typing, command execution, and web browsing, while ensuring safety through predefined limits and restrictions.

RAGMemory Class
Manages a memory system using Retrieval-Augmented Generation (RAG) with FAISS for efficient similarity searches and memory retrieval based on embeddings.

SystemState Class
Maintains the current state of the system, including metrics, active rules, pending actions, and the knowledge graph.

PatternDetectionAgent Class
Analyzes incoming data to detect patterns such as recurring elements, structural similarities, temporal patterns, and causal relationships using AI models.

RuleGenerationAgent Class
Generates new rules based on detected patterns, facilitating Alice's ability to adapt and learn autonomously.

AnalysisAgent Class
Evaluates the current system state to identify key metrics, areas needing improvement, recommended actions, and resource requirements.

WebInteractionAgent Class
Manages web interactions and browsing activities, integrating with the ComputerInteractionSystem for automated tasks.

NoveltySeekingAlgorithm Class
Implements algorithms to seek novel information, assess incompleteness in tasks, and enhance the knowledge graph by generating and integrating new rules.

PersistentStorage Class
Handles the saving and loading of persistent data, including RAG memory, rules, system state, and the knowledge graph, ensuring data longevity across sessions.

EnhancedLearningSystem Class
Integrates all components, managing the overall workflow of processing tasks, applying rules, saving state, and interacting with various agents to maintain and enhance system capabilities.

Streamlit Interface
Provides a user-friendly web interface for interacting with Alice, allowing users to input tasks, view system metrics, and monitor results in real-time.

Dependencies
Alice relies on several Python libraries and external tools. Ensure all dependencies are installed as specified.

Python Libraries
anthropic: For interacting with Anthropic's AI models.
openai: For interacting with OpenAI's APIs.
streamlit: For creating the web interface.
pyautogui: For automating mouse and keyboard interactions.
subprocess: For executing system commands.
os: For operating system interactions.
datetime: For handling date and time.
typing: For type annotations.
numpy: For numerical operations.
pickle: For serializing objects.
faiss: For efficient similarity search and clustering of dense vectors.
selenium: For automating web browser interactions.
time: For time-related functions.
logging: For logging system actions and errors.
networkx: For creating and managing knowledge graphs.
json: For handling JSON data.
asyncio: For asynchronous operations.
External Tools
Chrome WebDriver: Required for Selenium to automate Chrome browser interactions.
Logging
Alice maintains detailed logs of all system actions and errors to help with monitoring and debugging.

System Actions Log: Stored in system_actions.log.
Learning System Log: Stored in learning_system.log.
Ensure that these log files are monitored regularly to track the system's performance and identify any issues.

Contributing
Contributions are welcome! If you'd like to contribute to Alice, please follow these steps:

Fork the Repository: Click the "Fork" button at the top-right corner of the repository page.

Clone Your Fork:
git clone https://github.com/yourusername/alice-enhanced-learning-system.git
cd alice-enhanced-learning-system
Create a New Branch:
git checkout -b feature/your-feature-name
Make Your Changes: Implement your feature or bug fix.
Commit Your Changes:
git commit -m "Add feature: your feature description"
Push to Your Fork:
git push origin feature/your-feature-name
Open a Pull Request: Navigate to the original repository and open a pull request from your fork.

Please ensure your code follows the project's coding standards and includes appropriate tests.

License
This project is licensed under the MIT License.

