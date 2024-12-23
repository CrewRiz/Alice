"""
Alice - Enhanced Learning and Automation System
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from openai import OpenAI, AsyncOpenAI
import anthropic
import streamlit as st

from config import (
    REFERENCE_TIME, OPENAI_API_KEY, ANTHROPIC_API_KEY,
    setup_logging
)
from state_management import StateManager
from utility_management import UtilityManager
from events.event_system import EventManager, EventPriority
from security.security_manager import SecurityManager, SecurityContext, SecurityLevel
from monitoring.system_monitor import SystemMonitor
from validation.data_validation import ValidationManager, TaskType
from TimePerception import QuantumTime, QuantumTaskScheduler
from PersonalityGene import PersonalitySystem
from ComputerInteractionSystem1 import ComputerInteractionSystem
from AutomationSystem import AutomationSystem
from ProcessManager import ProcessManager
from DataManager import DataManager

class Alice:
    """
    Main class for the Alice system, integrating all components with improved
    organization and error handling.
    """
    
    def __init__(self):
        """Initialize Alice with all required components."""
        # Set up logging
        setup_logging()
        self.reference_time = REFERENCE_TIME
        
        # Initialize API clients
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
        
        # Initialize core components
        self.event_manager = EventManager()
        self.state_manager = StateManager()
        self.utility_manager = UtilityManager()
        self.security_manager = SecurityManager(self.event_manager)
        self.system_monitor = SystemMonitor(self.event_manager)
        self.validation_manager = ValidationManager()
        
        # Initialize time and scheduling components
        self.quantum_time = QuantumTime(self.state_manager)
        self.task_scheduler = QuantumTaskScheduler(self.quantum_time)
        
        # Initialize personality and interaction systems
        self.personality = PersonalitySystem()
        self.computer_interaction = ComputerInteractionSystem()
        
        # Initialize automation components
        self.automation_system = AutomationSystem(self.quantum_time)
        self.process_manager = ProcessManager(self.quantum_time)
        self.data_manager = DataManager()
        
        logging.info("Alice system initialized")
        
    async def initialize(self):
        """Initialize all system components."""
        try:
            # Initialize event system
            await self.event_manager.initialize()
            
            # Start monitoring
            monitor_task = asyncio.create_task(self.system_monitor.start())
            
            # Configure security rules
            self._configure_security_rules()
            
            # Emit system startup event
            await self.event_manager.emit(
                'system.startup',
                {'timestamp': datetime.now().isoformat()},
                EventPriority.HIGH
            )
            
            logging.info("Alice system startup completed")
            
        except Exception as e:
            logging.error(f"System initialization failed: {str(e)}")
            raise
            
    def _configure_security_rules(self):
        """Configure initial security rules."""
        # Configure operation security levels
        self.security_manager.configure_operation(
            'system.shutdown',
            SecurityLevel.CRITICAL
        )
        self.security_manager.configure_operation(
            'automation.execute',
            SecurityLevel.HIGH
        )
        self.security_manager.configure_operation(
            'data.modify',
            SecurityLevel.HIGH
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task with comprehensive validation and monitoring."""
        try:
            # Validate task data
            task = self.validation_manager.validate_task(task_data)
            
            # Create security context
            context = SecurityContext(
                level=SecurityLevel.MEDIUM,  # Default level
                source=task_data.get('source', 'system'),
                timestamp=datetime.now(),
                metadata=task.metadata
            )
            
            # Validate security
            await self.security_manager.validate_operation(
                f"{task.type}.execute",
                context
            )
            
            # Update state
            self.state_manager.current_task = task.id
            self.state_manager.update({
                'status': 'processing',
                'total_tasks': self.state_manager.metrics['total_tasks'] + 1
            })
            
            # Schedule and execute task
            scheduled_task = await self.task_scheduler.schedule_task(task)
            result = await self._execute_task(scheduled_task)
            
            # Update metrics on success
            if result.get('success'):
                self.state_manager.update({
                    'completed_tasks': self.state_manager.metrics['completed_tasks'] + 1,
                    'status': 'ready'
                })
            
            # Evaluate utility
            utility = self.utility_manager.evaluate(self.state_manager)
            
            # Trigger self-improvement if needed
            if self.utility_manager.needs_improvement():
                await self._trigger_self_improvement()
            
            return {
                'success': result.get('success', False),
                'result': result.get('result'),
                'utility': utility
            }
            
        except Exception as e:
            # Track error
            self.system_monitor.track_error(e, {
                'task_id': task_data.get('id'),
                'task_type': task_data.get('type')
            })
            
            # Update state
            self.state_manager.update({
                'status': 'error',
                'error_count': self.state_manager.operational_state['error_count'] + 1
            })
            
            return {
                'success': False,
                'error': str(e),
                'utility': self.utility_manager.evaluate(self.state_manager)
            }
            
    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task based on its type."""
        try:
            if task['type'] == TaskType.AUTOMATION:
                return await self.automation_system.execute_task(task)
                
            elif task['type'] == TaskType.INTERACTION:
                return await self._handle_interaction(task)
                
            elif task['type'] == TaskType.LEARNING:
                return await self._handle_learning(task)
                
            else:
                return await self._handle_generic_task(task)
                
        except Exception as e:
            logging.error(f"Task execution failed: {str(e)}")
            raise
            
    async def cleanup(self):
        """Clean up system resources."""
        try:
            await self.automation_system.cleanup()
            await self.process_manager.cleanup()
            await self.data_manager.cleanup()
            await self.event_manager.cleanup()
            logging.info("Alice system cleanup completed")
            
        except Exception as e:
            logging.error(f"Cleanup failed: {str(e)}")
            raise

# Streamlit interface
def create_interface():
    """Create Streamlit interface for Alice system."""
    st.title("Alice - Enhanced Learning System")
    
    # Initialize Alice if not exists
    if 'alice' not in st.session_state:
        st.session_state.alice = Alice()
        asyncio.run(st.session_state.alice.initialize())
        
    # Task input
    task_input = st.text_input("Enter task:")
    task_type = st.selectbox(
        "Task type",
        [t.value for t in TaskType]
    )
    
    if st.button("Process Task"):
        task = {
            'id': datetime.now().isoformat(),
            'type': task_type,
            'description': task_input
        }
        result = asyncio.run(st.session_state.alice.process_task(task))
        st.write("Result:", result)
        
    # System state
    if st.checkbox("Show System State"):
        state = st.session_state.alice.state_manager.get_summary()
        st.write("System State:", state)
        
    # Utility history
    if st.checkbox("Show Utility History"):
        history = st.session_state.alice.utility_manager.get_utility_history()
        st.line_chart(history)
        
    # Monitoring
    if st.checkbox("Show System Metrics"):
        metrics = st.session_state.alice.system_monitor.performance_monitor.metrics.get_metrics()
        st.write("System Metrics:", metrics)

def main():
    """Main entry point."""
    create_interface()

if __name__ == "__main__":
    main()
