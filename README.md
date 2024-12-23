# Alice - Enhanced Learning and Automation System

Alice is an advanced AI-powered system that combines automation, learning, and interaction capabilities with robust security and monitoring features.

## Features

### Core Components
- **Service Layer**: Standardized service interactions with base service implementation
- **Event System**: Asynchronous event processing with priority-based handling
- **Monitoring**: Real-time system metrics, performance tracking, and error monitoring
- **Security**: Operation-level security validation and source blocking
- **Data Validation**: Comprehensive input validation and schema enforcement

### Key Systems
- **Time Perception**: Quantum-aware time management
- **Personality System**: Adaptive behavior and learning
- **Automation**: Task automation with workflow templates
- **Process Management**: Efficient process handling and resource management
- **Computer Interaction**: Safe and controlled system interactions

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key
- Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/CrewRiz/Alice.git
cd Alice
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.template .env
```
Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Running Tests
```bash
pytest Alice/tests/
```

## Architecture

### Service Layer
- `BaseService`: Abstract base class for all services
- Standardized initialization and cleanup
- Health check mechanisms

### Event System
- `EventBus`: Event subscription and publishing
- `EventManager`: Event creation and emission
- Priority-based event processing
- Asynchronous event handling

### Monitoring System
- `MetricsCollector`: System performance metrics
- `PerformanceMonitor`: CPU, memory, and disk usage tracking
- `ErrorTracker`: Error monitoring and analysis
- `SystemMonitor`: Centralized monitoring coordination

### Security Management
- `SecurityManager`: Operation validation
- `SecurityContext`: Security-level tracking
- Source blocking capabilities
- Security violation logging

### Data Validation
- Task validation
- Input sanitization
- Schema enforcement
- Operation validation

## Usage

```python
from Alice.Alice import Alice

# Initialize Alice
alice = Alice()
await alice.initialize()

# Process a task
result = await alice.process_task({
    'id': 'task_id',
    'type': 'automation',
    'description': 'Task description'
})

# Cleanup
await alice.cleanup()
```

## Development

### Running Tests
The test suite includes:
- Unit tests
- Integration tests
- Performance tests
- Security tests

```bash
# Run all tests
pytest

# Run specific test category
pytest Alice/tests/test_core.py
```

### Adding New Features
1. Implement the feature in the appropriate module
2. Add corresponding tests
3. Update documentation
4. Submit a pull request

## Security

- API keys and sensitive data are managed through environment variables
- Security levels control operation access
- Source blocking prevents unauthorized access
- Comprehensive security validation

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- The Python community for excellent tools and libraries
