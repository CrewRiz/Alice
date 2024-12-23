import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path

from AutomationSystem import AutomationType, AutomationTask
from AdvancedInteractions import InteractionMode

class BuilderError(Exception):
    """Base class for builder errors."""
    pass

class ValidationError(BuilderError):
    """Raised when validation fails."""
    pass

class ConfigurationError(BuilderError):
    """Raised when configuration is invalid."""
    pass

class AutomationBuilder:
    """User-friendly builder for creating automation tasks."""
    
    def __init__(self):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:45:08-06:00")
        self._reset()
        
    def _reset(self):
        """Reset the builder state."""
        self.current_task = {
            'automation': None,
            'parameters': {},
            'conditions': {},
            'callbacks': {},
            'timeout': 60.0,
            'retry_count': 3,
            'quantum_sensitive': True
        }
        
    def ui(self) -> 'UIAutomationBuilder':
        """Start building a UI automation task."""
        self.current_task['automation'] = 'UI_AUTOMATION'
        return UIAutomationBuilder(self)
        
    def process(self) -> 'ProcessAutomationBuilder':
        """Start building a process automation task."""
        self.current_task['automation'] = 'PROCESS_AUTOMATION'
        return ProcessAutomationBuilder(self)
        
    def data(self) -> 'DataAutomationBuilder':
        """Start building a data automation task."""
        self.current_task['automation'] = 'DATA_AUTOMATION'
        return DataAutomationBuilder(self)
        
    def workflow(self) -> 'WorkflowAutomationBuilder':
        """Start building a workflow automation task."""
        self.current_task['automation'] = 'WORKFLOW_AUTOMATION'
        return WorkflowAutomationBuilder(self)
        
    def learning(self) -> 'LearningAutomationBuilder':
        """Start building a learning automation task."""
        self.current_task['automation'] = 'LEARNING_AUTOMATION'
        return LearningAutomationBuilder(self)

class BaseAutomationBuilder:
    """Base class for all automation builders."""
    
    def __init__(self, parent: AutomationBuilder):
        self.parent = parent
        
    def build(self) -> Dict[str, Any]:
        """Build and validate the automation task."""
        try:
            self._validate()
            return AutomationTask(
                type=self.parent.current_task['automation'],
                parameters=self.parent.current_task['parameters'].copy(),
                timeout=self.parent.current_task.get('timeout'),
                retries=self.parent.current_task.get('retry_count', 0),
                quantum_sensitive=self.parent.current_task.get('quantum_sensitive', False)
            )
        except Exception as e:
            raise BuilderError(f"Failed to build task: {str(e)}")
            
    def _validate(self):
        """Validate the current configuration."""
        pass
        
    def with_timeout(self, seconds: float) -> 'BaseAutomationBuilder':
        """Set the timeout for the task."""
        self.parent.current_task['timeout'] = seconds
        return self
        
    def with_retries(self, count: int) -> 'BaseAutomationBuilder':
        """Set the number of retries for the task."""
        if count < 0:
            raise ValidationError("Retries must be non-negative")
        self.parent.current_task['retry_count'] = count
        return self
        
    def quantum_sensitive(self, enabled: bool = True) -> 'BaseAutomationBuilder':
        """Set whether the task is quantum sensitive."""
        self.parent.current_task['quantum_sensitive'] = enabled
        return self
        
    def with_condition(self, name: str, value: Any) -> 'BaseAutomationBuilder':
        """Add a condition to the task."""
        self.parent.current_task['conditions'][name] = value
        return self
        
    def with_callback(self, event: str, callback: Callable) -> 'BaseAutomationBuilder':
        """Add a callback for task events."""
        self.parent.current_task['callbacks'][event] = callback
        return self

class UIAutomationBuilder(BaseAutomationBuilder):
    """Builder for UI automation tasks."""
    
    def _validate(self):
        """Validate UI automation configuration."""
        params = self.parent.current_task['parameters']
        if 'action' not in params:
            raise ValidationError("UI automation requires an action")
            
        action = params['action']
        if action == 'click':
            if 'target_type' not in params:
                raise ValidationError("Click action requires a target type")
            if params['target_type'] == 'image' and 'target_image' not in params:
                raise ValidationError("Image target requires target_image parameter")
            if params['target_type'] == 'text' and 'target_text' not in params:
                raise ValidationError("Text target requires target_text parameter")
                
        elif action == 'type' and 'text' not in params:
            raise ValidationError("Type action requires text parameter")
            
        elif action == 'hotkey' and 'keys' not in params:
            raise ValidationError("Hotkey action requires keys parameter")
            
    def click_image(self, image_path: str, confidence: float = 0.9) -> 'UIAutomationBuilder':
        """Click on an image on screen."""
        self.parent.current_task['parameters'].update({
            'target_type': 'image',
            'target_image': image_path,
            'action': 'click',
            'confidence': confidence
        })
        return self
        
    def click_text(self, text: str, partial_match: bool = False) -> 'UIAutomationBuilder':
        """Click on text on screen."""
        self.parent.current_task['parameters'].update({
            'target_type': 'text',
            'target_text': text,
            'action': 'click',
            'partial_match': partial_match
        })
        return self
        
    def type_text(self, text: str, interval: float = 0.1) -> 'UIAutomationBuilder':
        """Type text with natural timing."""
        self.parent.current_task['parameters'].update({
            'target_type': 'keyboard',
            'text': text,
            'interval': interval
        })
        return self

    def press_keys(self, *keys: str) -> 'UIAutomationBuilder':
        """Press multiple keys in sequence."""
        self.parent.current_task['parameters'].update({
            'target_type': 'keyboard',
            'action': 'press',
            'keys': list(keys)
        })
        return self

    def hold_key(self, key: str, duration: float) -> 'UIAutomationBuilder':
        """Hold a key for a specified duration."""
        self.parent.current_task['parameters'].update({
            'target_type': 'keyboard',
            'action': 'hold',
            'key': key,
            'duration': duration
        })
        return self

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> 'UIAutomationBuilder':
        """Move mouse to specific coordinates."""
        self.parent.current_task['parameters'].update({
            'target_type': 'mouse',
            'action': 'move',
            'x': x,
            'y': y,
            'duration': duration
        })
        return self

    def scroll(self, amount: int, direction: str = 'down') -> 'UIAutomationBuilder':
        """Scroll the mouse wheel."""
        self.parent.current_task['parameters'].update({
            'target_type': 'mouse',
            'action': 'scroll',
            'amount': amount,
            'direction': direction
        })
        return self

    def right_click(self, target: str = None) -> 'UIAutomationBuilder':
        """Right click at current position or on target."""
        self.parent.current_task['parameters'].update({
            'target_type': 'mouse',
            'action': 'right_click',
            'target': target
        })
        return self

    def double_click(self, target: str = None) -> 'UIAutomationBuilder':
        """Double click at current position or on target."""
        self.parent.current_task['parameters'].update({
            'target_type': 'mouse',
            'action': 'double_click',
            'target': target
        })
        return self

    def hover(self, target: str, duration: float = 0.5) -> 'UIAutomationBuilder':
        """Hover over a target."""
        self.parent.current_task['parameters'].update({
            'target_type': 'mouse',
            'action': 'hover',
            'target': target,
            'duration': duration
        })
        return self

    def wait_for_color(self, x: int, y: int, color: tuple, 
                      tolerance: int = 10) -> 'UIAutomationBuilder':
        """Wait for a specific color at coordinates."""
        self.parent.current_task['parameters'].update({
            'target_type': 'color',
            'action': 'wait',
            'x': x,
            'y': y,
            'color': color,
            'tolerance': tolerance
        })
        return self

    def capture_screen(self, region: tuple = None) -> 'UIAutomationBuilder':
        """Capture screen or region."""
        self.parent.current_task['parameters'].update({
            'target_type': 'screen',
            'action': 'capture',
            'region': region
        })
        return self

    def drag_drop(self, start_image: str, end_image: str) -> 'UIAutomationBuilder':
        """Perform drag and drop operation."""
        self.parent.current_task['parameters'].update({
            'target_type': 'gesture',
            'action': 'drag_drop',
            'start_image': start_image,
            'end_image': end_image
        })
        return self
        
    def wait_for_image(self, image_path: str, timeout: float = 10.0) -> 'UIAutomationBuilder':
        """Wait for an image to appear."""
        self.parent.current_task['parameters'].update({
            'target_type': 'image',
            'target_image': image_path,
            'action': 'wait',
            'timeout': timeout
        })
        return self

class ProcessAutomationBuilder(BaseAutomationBuilder):
    """Builder for process automation tasks."""
    
    def run_command(self, command: str, args: List[str] = None) -> 'ProcessAutomationBuilder':
        """Run a system command."""
        self.parent.current_task['parameters'].update({
            'process_type': 'command',
            'command': command,
            'args': args or []
        })
        return self
        
    def start_service(self, service_name: str) -> 'ProcessAutomationBuilder':
        """Start a system service."""
        self.parent.current_task['parameters'].update({
            'process_type': 'service',
            'action': 'start',
            'service_name': service_name
        })
        return self
        
    def stop_service(self, service_name: str) -> 'ProcessAutomationBuilder':
        """Stop a system service."""
        self.parent.current_task['parameters'].update({
            'process_type': 'service',
            'action': 'stop',
            'service_name': service_name
        })
        return self
        
    def run_batch(self, script_path: str, args: List[str] = None) -> 'ProcessAutomationBuilder':
        """Run a batch script."""
        self.parent.current_task['parameters'].update({
            'process_type': 'batch',
            'script_path': script_path,
            'args': args or []
        })
        return self

    def run_python_script(self, script_path: str, args: List[str] = None,
                         env: Dict[str, str] = None) -> 'ProcessAutomationBuilder':
        """Run a Python script."""
        self.parent.current_task['parameters'].update({
            'process_type': 'python',
            'script_path': script_path,
            'args': args or [],
            'env': env or {}
        })
        return self

    def run_powershell(self, script: str) -> 'ProcessAutomationBuilder':
        """Run a PowerShell command."""
        self.parent.current_task['parameters'].update({
            'process_type': 'powershell',
            'script': script
        })
        return self

    def monitor_process(self, process_name: str, 
                       conditions: Dict[str, Any]) -> 'ProcessAutomationBuilder':
        """Monitor a process for specific conditions."""
        self.parent.current_task['parameters'].update({
            'process_type': 'monitor',
            'process_name': process_name,
            'conditions': conditions
        })
        return self

class DataAutomationBuilder(BaseAutomationBuilder):
    """Builder for data automation tasks."""
    
    def extract_from_web(self, url: str, selectors: Dict[str, str]) -> 'DataAutomationBuilder':
        """Extract data from a webpage."""
        self.parent.current_task['parameters'].update({
            'data_type': 'extraction',
            'source': 'web',
            'url': url,
            'selectors': selectors
        })
        return self
        
    def transform_json(self, input_path: str, output_path: str, 
                      transformations: List[Dict[str, Any]]) -> 'DataAutomationBuilder':
        """Transform JSON data."""
        self.parent.current_task['parameters'].update({
            'data_type': 'transformation',
            'format': 'json',
            'input_path': input_path,
            'output_path': output_path,
            'transformations': transformations
        })
        return self
        
    def validate_data(self, data_path: str, schema: Dict[str, Any]) -> 'DataAutomationBuilder':
        """Validate data against a schema."""
        self.parent.current_task['parameters'].update({
            'data_type': 'validation',
            'data_path': data_path,
            'schema': schema
        })
        return self

    def extract_table(self, url: str, table_selector: str) -> 'DataAutomationBuilder':
        """Extract table data from webpage."""
        self.parent.current_task['parameters'].update({
            'data_type': 'extraction',
            'source': 'web_table',
            'url': url,
            'selector': table_selector
        })
        return self

    def monitor_file(self, file_path: str, pattern: str) -> 'DataAutomationBuilder':
        """Monitor a file for changes matching pattern."""
        self.parent.current_task['parameters'].update({
            'data_type': 'monitor',
            'file_path': file_path,
            'pattern': pattern
        })
        return self

    def sync_folders(self, source: str, destination: str,
                    patterns: List[str] = None) -> 'DataAutomationBuilder':
        """Synchronize folders."""
        self.parent.current_task['parameters'].update({
            'data_type': 'sync',
            'source': source,
            'destination': destination,
            'patterns': patterns
        })
        return self

class WorkflowAutomationBuilder(BaseAutomationBuilder):
    """Builder for workflow automation tasks."""
    
    def __init__(self, parent: AutomationBuilder):
        super().__init__(parent)
        self.steps: List[Dict[str, Any]] = []
        
    def add_step(self, step: Dict[str, Any]) -> 'WorkflowAutomationBuilder':
        """Add a step to the workflow."""
        self.steps.append(step)
        return self
        
    def run_sequential(self) -> 'WorkflowAutomationBuilder':
        """Run steps sequentially."""
        self.parent.current_task['parameters'].update({
            'workflow_type': 'sequential',
            'steps': self.steps
        })
        return self
        
    def run_parallel(self) -> 'WorkflowAutomationBuilder':
        """Run steps in parallel."""
        self.parent.current_task['parameters'].update({
            'workflow_type': 'parallel',
            'steps': self.steps
        })
        return self
        
    def run_conditional(self, condition: Callable[[Dict[str, Any]], bool]) -> 'WorkflowAutomationBuilder':
        """Run steps conditionally."""
        self.parent.current_task['parameters'].update({
            'workflow_type': 'conditional',
            'steps': self.steps,
            'condition': condition
        })
        return self

class LearningAutomationBuilder(BaseAutomationBuilder):
    """Builder for learning automation tasks."""
    
    def learn_pattern(self, source_type: str, pattern_name: str) -> 'LearningAutomationBuilder':
        """Learn a new automation pattern."""
        self.parent.current_task['parameters'].update({
            'learning_type': 'pattern',
            'source_type': source_type,
            'pattern_name': pattern_name
        })
        return self
        
    def optimize_workflow(self, workflow_id: str) -> 'LearningAutomationBuilder':
        """Optimize an existing workflow."""
        self.parent.current_task['parameters'].update({
            'learning_type': 'optimization',
            'workflow_id': workflow_id
        })
        return self
        
    def analyze_behavior(self, behavior_type: str) -> 'LearningAutomationBuilder':
        """Analyze and learn from behavior patterns."""
        self.parent.current_task['parameters'].update({
            'learning_type': 'behavior',
            'behavior_type': behavior_type
        })
        return self

# Example usage:
"""
# Create a builder
builder = AutomationBuilder()

# Build a UI automation task
ui_task = (builder.ui()
    .click_image('button.png')
    .with_timeout(30)
    .with_retries(5)
    .quantum_sensitive()
    .build())

# Build a workflow automation task
workflow_task = (builder.workflow()
    .add_step(builder.ui().click_text('Login').build())
    .add_step(builder.ui().type_text('username').build())
    .add_step(builder.ui().type_text('password').build())
    .add_step(builder.ui().click_text('Submit').build())
    .run_sequential()
    .with_timeout(60)
    .build())

# Build a data automation task
data_task = (builder.data()
    .extract_from_web(
        'https://example.com',
        {'title': 'h1', 'content': '.main-content'}
    )
    .with_timeout(30)
    .build())

# Execute tasks
await computer_system.execute_action(ui_task)
await computer_system.execute_action(workflow_task)
await computer_system.execute_action(data_task)
"""
